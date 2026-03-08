// Git service — wraps git2 operations
// See: /arch/adr-001-tauri-v2-migration.md

use std::collections::HashMap;
use std::path::Path;
use git2::{Repository, Signature, IndexAddOption, StatusOptions};
use crate::models::commit::CommitInfo;

/// Initialize a git repository at the given path (no-op if already a repo)
pub fn init_repo(repo_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let path = Path::new(repo_path);
    if path.join(".git").exists() {
        return Ok(());
    }
    Repository::init(path)?;
    Ok(())
}

/// List all commits across all branches in the repository
pub fn list_commits(repo_path: &str) -> Result<Vec<CommitInfo>, Box<dyn std::error::Error>> {
    let repo = Repository::open(repo_path)?;

    // Get current HEAD commit SHA
    let head_sha = repo.head()
        .ok()
        .and_then(|h| h.peel_to_commit().ok())
        .map(|c| c.id().to_string()[..8].to_string());

    // Build a map of commit SHA -> branch names
    let mut branch_map: HashMap<String, Vec<String>> = HashMap::new();
    if let Ok(branches) = repo.branches(Some(git2::BranchType::Local)) {
        for branch_result in branches {
            let (branch, _) = branch_result?;
            let branch_name = branch.name()?.unwrap_or("unknown").to_string();
            if let Some(commit) = branch.get().peel_to_commit().ok() {
                let sha = commit.id().to_string()[..8].to_string();
                branch_map.entry(sha).or_default().push(branch_name);
            }
        }
    }

    let mut revwalk = repo.revwalk()?;
    revwalk.push_glob("*")?;
    revwalk.set_sorting(git2::Sort::TOPOLOGICAL | git2::Sort::TIME)?;

    let mut commits: Vec<CommitInfo> = Vec::new();

    for oid in revwalk {
        let oid = oid?;
        let commit = repo.find_commit(oid)?;
        let hex_sha = oid.to_string()[..8].to_string();

        let is_current = Some(&hex_sha) == head_sha.as_ref();

        let info = CommitInfo {
            branches: branch_map.get(&hex_sha).cloned().unwrap_or_default(),
            hex_sha,
            author: commit.author().name().unwrap_or("Unknown").to_string(),
            message: commit.message().unwrap_or("").trim().to_string(),
            parents: commit
                .parent_ids()
                .map(|id| id.to_string()[..8].to_string())
                .collect(),
            timestamp: commit.time().seconds(),
            is_current,
        };
        commits.push(info);
    }

    Ok(commits)
}

/// Get all local branch names
pub fn get_branches(repo_path: &str) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let repo = Repository::open(repo_path)?;
    let branches = repo.branches(Some(git2::BranchType::Local))?;

    let mut branch_names = Vec::new();
    for branch in branches {
        let (branch, _) = branch?;
        if let Some(name) = branch.name()? {
            branch_names.push(name.to_string());
        }
    }

    Ok(branch_names)
}

/// Create a commit with the given message (stages all changes first)
pub fn create_commit(repo_path: &str, message: &str) -> Result<String, Box<dyn std::error::Error>> {
    let repo = Repository::open(repo_path)?;

    // Stage all changes (add all)
    let mut index = repo.index()?;
    index.add_all(["*"].iter(), IndexAddOption::DEFAULT, None)?;

    // Also remove deleted files from index
    let mut opts = StatusOptions::new();
    opts.include_untracked(false);
    let statuses = repo.statuses(Some(&mut opts))?;
    for entry in statuses.iter() {
        if entry.status().is_wt_deleted() {
            if let Some(path) = entry.path() {
                index.remove_path(Path::new(path))?;
            }
        }
    }

    index.write()?;
    let tree_id = index.write_tree()?;
    let tree = repo.find_tree(tree_id)?;

    let sig = Signature::now("Git Game Save Manager", "save@manager.local")?;

    // Get parent commit if exists
    let parent_commit = repo.head().ok().and_then(|h| h.peel_to_commit().ok());
    let parents: Vec<&git2::Commit> = parent_commit.iter().collect();

    let oid = repo.commit(Some("HEAD"), &sig, &sig, message, &tree, &parents)?;

    Ok(oid.to_string()[..8].to_string())
}

/// Checkout to a specific commit (detached HEAD)
pub fn checkout_commit(repo_path: &str, commit_sha: &str) -> Result<(), Box<dyn std::error::Error>> {
    let repo = Repository::open(repo_path)?;

    // Find the commit by partial SHA
    let oid = repo.revparse_single(commit_sha)?.id();
    let commit = repo.find_commit(oid)?;

    // Checkout the tree
    let tree = commit.tree()?;
    repo.checkout_tree(tree.as_object(), Some(
        git2::build::CheckoutBuilder::new()
            .force()
    ))?;

    // Set HEAD to detached at this commit
    repo.set_head_detached(oid)?;

    Ok(())
}
