// Git service — wraps git2 operations
// See: /arch/adr-001-tauri-v2-migration.md

use std::collections::HashMap;
use std::path::Path;
use git2::{Repository, Signature, IndexAddOption, StatusOptions};
use crate::models::commit::CommitInfo;

// --- Repository Operations ---

/// Initialize a new Git repository
pub fn init_repo(repo_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Initializing repo at: {}", repo_path);
    let path = Path::new(repo_path);
    if path.join(".git").exists() {
        return Ok(());
    }
    Repository::init(path)?;
    Ok(())
}

/// Get all commits from the repository (DAG topology)
pub fn list_commits(repo_path: &str) -> Result<Vec<CommitInfo>, Box<dyn std::error::Error>> {
    // println!("[GitService] Listing commits for: {}", repo_path); // Might be too noisy
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
    // Push BOTH HEAD and all named refs to ensure we include commits
    // reachable from detached HEAD (push_glob only walks refs/*)
    revwalk.push_head()?;
    revwalk.push_glob("*")?;
    revwalk.set_sorting(git2::Sort::TOPOLOGICAL | git2::Sort::TIME)?;

    let mut commits: Vec<CommitInfo> = Vec::new();
    let mut seen = std::collections::HashSet::new();

    for oid in revwalk {
        let oid = oid?;
        if !seen.insert(oid) {
            continue; // Skip duplicates
        }
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
    println!("[GitService] Getting branches for: {}", repo_path);
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

/// Create a new branch at a specific commit and switch to it
pub fn create_branch(repo_path: &str, branch_name: &str, commit_sha: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Creating branch '{}' at commit {} in {}", branch_name, commit_sha, repo_path);
    let repo = Repository::open(repo_path)?;
    let oid = repo.revparse_single(commit_sha)?.id();
    let commit = repo.find_commit(oid)?;

    // Create the branch
    repo.branch(branch_name, &commit, false)?;

    // Switch to the new branch
    let refname = format!("refs/heads/{}", branch_name);
    repo.set_head(&refname)?;
    repo.checkout_tree(commit.as_object(), Some(git2::build::CheckoutBuilder::new().force()))?;

    println!("[GitService] Branch '{}' created and checked out.", branch_name);
    Ok(())
}

/// Switch to an existing branch
pub fn switch_branch(repo_path: &str, branch_name: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Switching to branch '{}' in {}", branch_name, repo_path);
    let repo = Repository::open(repo_path)?;

    let refname = format!("refs/heads/{}", branch_name);
    let obj = repo.revparse_single(&refname)?;
    repo.checkout_tree(&obj, Some(git2::build::CheckoutBuilder::new().force()))?;
    repo.set_head(&refname)?;

    println!("[GitService] Switched to branch '{}'.", branch_name);
    Ok(())
}

/// Create a new commit
pub fn create_commit(repo_path: &str, message: &str) -> Result<String, Box<dyn std::error::Error>> {
    println!("[GitService] Creating new commit: '{}' at {}", message, repo_path);
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

/// Checkout a specific commit
pub fn checkout_commit(repo_path: &str, commit_sha: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Checking out commit: {} at {}", commit_sha, repo_path);
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

/// Reset hard to a specific commit (throws away subsequent history)
pub fn reset_hard_commit(repo_path: &str, commit_sha: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Resetting hard to commit: {} at {}", commit_sha, repo_path);
    let repo = Repository::open(repo_path)?;

    let oid = repo.revparse_single(commit_sha)?.id();
    let commit = repo.find_commit(oid)?;
    let tree = commit.tree()?;

    // Reset hard!
    repo.reset(commit.as_object(), git2::ResetType::Hard, Some(
        git2::build::CheckoutBuilder::new()
            .force()
            .remove_untracked(true)
    ))?;

    // We also want to ensure HEAD points firmly to this commit
    // If we're detached, we set it detached. If we're on a branch, reset updates the branch reference automatically.
    if repo.head_detached().unwrap_or(true) {
        repo.set_head_detached(oid)?;
    }

    Ok(())
}

/// Amend the message of a specific historical or current commit
/// This performs a programmatic rebase if the commit is not HEAD.
pub fn amend_commit(repo_path: &str, target_sha: &str, new_message: &str) -> Result<String, Box<dyn std::error::Error>> {
    println!("[GitService] Amending commit {} with new message: '{}'", target_sha, new_message);
    let repo = Repository::open(repo_path)?;
    let target_oid = repo.revparse_single(target_sha)?.id();

    // 1. Get current HEAD
    let head_ref = repo.head()?;
    let is_branch = head_ref.is_branch();
    let branch_name = if is_branch {
        head_ref.name().map(String::from)
    } else {
        None
    };
    let head_commit = head_ref.peel_to_commit()?;
    let head_oid = head_commit.id();

    // Fast path: amending the current HEAD is trivial and quick
    if head_oid == target_oid {
        println!("[GitService] Target commit is HEAD. Executing fast amend.");
        let sig = Signature::now("Git Game Save Manager", "save@manager.local")?;
        let new_oid = head_commit.amend(
            Some("HEAD"),
            Some(&sig),
            Some(&sig),
            None,
            Some(new_message),
            None // Use same tree
        )?;
        println!("[GitService] Fast amend created new OID: {}", new_oid.to_string()[..8].to_string());

        // CRITICAL: also update any branch refs that pointed to the old HEAD
        let branches = repo.branches(Some(git2::BranchType::Local))?;
        for branch_result in branches {
            let (branch, _) = branch_result?;
            if let Some(target) = branch.get().target() {
                if target == head_oid {
                    let ref_name = branch.get().name().unwrap_or("").to_string();
                    if !ref_name.is_empty() {
                        println!("[GitService] Updating stale branch '{}' from {} to {}", ref_name, head_oid.to_string()[..8].to_string(), new_oid.to_string()[..8].to_string());
                        repo.reference(&ref_name, new_oid, true, "Fast amend: update branch pointer")?;
                    }
                }
            }
        }

        return Ok(new_oid.to_string()[..8].to_string());
    }

    // 2. Complex path: Target is in history. We must rebase.
    // First, verify the target is actually an ancestor of HEAD to safely linear-rebase
    let is_ancestor = repo.graph_descendant_of(head_oid, target_oid)?;
    if !is_ancestor {
        println!("[GitService] Rejecting amend: Commit {} is not an ancestor of current HEAD ({}).", target_oid, head_oid);
        return Err("当前存档不是最新存档的直系祖先，无法进行安全重写。要想修改该存档，请先将其切换为当前存档。".into());
    }

    // 3. Collect the path from HEAD down to the CHILD of target_commit
    println!("[GitService] Collecting rebase path from {} down to {}", head_oid, target_oid);
    let mut revwalk = repo.revwalk()?;
    revwalk.push(head_oid)?;
    revwalk.hide(target_oid)?;
    revwalk.set_sorting(git2::Sort::TOPOLOGICAL | git2::Sort::REVERSE)?;

    let mut commits_to_replay = Vec::new();
    for oid in revwalk {
        let oid = oid.map_err(|e| format!("Failed revwalk iteration: {}", e))?;
        commits_to_replay.push(oid);
    }

    println!("[GitService] Initiating Programmatic Rebase. Commits to replay: {}", commits_to_replay.len());

    // 4. Checkout the target commit in detached state
    println!("[GitService] Detaching HEAD at target commit.");
    repo.set_head_detached(target_oid).map_err(|e| format!("Failed to detach head: {}", e))?;
    let target_commit = repo.find_commit(target_oid)?;
    repo.checkout_tree(target_commit.as_object(), Some(git2::build::CheckoutBuilder::new().force()))
        .map_err(|e| format!("Failed checkout_tree on detaching head: {}", e))?;

    // 5. Amend the target commit
    println!("[GitService] Amending target detached HEAD.");
    let sig = Signature::now("Git Game Save Manager", "save@manager.local")?;
    let amended_target_oid = target_commit.amend(
        Some("HEAD"),
        Some(&sig),
        Some(&sig),
        None,
        Some(new_message),
        None, // Use same tree
    ).map_err(|e| format!("Failed to amend detached head: {}", e))?;
    
    // Safety check tracking our new ascending HEAD
    let mut current_parent_oid = amended_target_oid;
    
    println!("[GitService] Replaying commits...");

    // 6. Replay (Cherry-pick) collected commits on top of the new ascending HEAD
    for oid in commits_to_replay {
        println!("[GitService] Cherry-picking commit {} onto {}", oid, current_parent_oid);
        let commit_to_replay = repo.find_commit(oid)
            .map_err(|e| format!("Cherry-pick find commit failed: {}", e))?;
        
        let parent_commit = repo.find_commit(current_parent_oid)?;
        let mut index = repo.cherrypick_commit(&commit_to_replay, &parent_commit, 0, None)
            .map_err(|e| format!("Cherry-pick operation failed on commit {}: {}", oid, e))?;
        
        if index.has_conflicts() {
            return Err(format!("Conflict detected during programmatic rebase at commit {}", oid).into());
        }

        // Write the new tree from the cherry-pick index
        let tree_oid = index.write_tree_to(&repo)
            .map_err(|e| format!("Failed writing tree after cherry-pick: {}", e))?;
        let tree = repo.find_tree(tree_oid)?;
        
        // Re-create the commit
        let author_sig = commit_to_replay.author();
        let committer_sig = commit_to_replay.committer();
        let message = commit_to_replay.message().unwrap_or("");
        
        current_parent_oid = repo.commit(
            Some("HEAD"),
            &author_sig,
            &committer_sig,
            message,
            &tree,
            &[&parent_commit]
        ).map_err(|e| format!("Failed committing replayed node: {}", e))?;

        // Update working directory progressively
        let current_commit_obj = repo.find_commit(current_parent_oid)?;
        repo.checkout_tree(current_commit_obj.as_object(), Some(git2::build::CheckoutBuilder::new().force()))
            .map_err(|e| format!("Failed repo.checkout_tree progressive step: {}", e))?;
        println!("  -> Replayed commit: {}", oid.to_string()[..8].to_string());
    }

    // 7. Update all references to ensure consistency
    // Always find branches that pointed to the OLD head and update them to the NEW replayed tip
    let branches = repo.branches(Some(git2::BranchType::Local))?;
    for branch_result in branches {
        let (branch, _) = branch_result?;
        if let Some(target) = branch.get().target() {
            if target == head_oid {
                let ref_name = branch.get().name().unwrap_or("").to_string();
                if !ref_name.is_empty() {
                    println!("[GitService] Updating stale branch '{}' from {} to {}", ref_name, head_oid.to_string()[..8].to_string(), current_parent_oid.to_string()[..8].to_string());
                    repo.reference(&ref_name, current_parent_oid, true, "Programmatic rebase: update branch pointer")?;
                }
            }
        }
    }

    // If we were on a named branch, restore HEAD to point to it
    if let Some(ref_name) = branch_name {
        println!("[GitService] Restoring HEAD to branch '{}'", ref_name);
        repo.set_head(&ref_name)?;
    } else {
        // Detached HEAD: just make sure it points to the final replayed commit
        println!("[GitService] Updating detached HEAD to {}", current_parent_oid.to_string()[..8].to_string());
        repo.set_head_detached(current_parent_oid)?;
    }

    println!("[GitService] Programmatic rebase completed successfully.");
    Ok(amended_target_oid.to_string()[..8].to_string())
}

/// Delete a specific commit from history by replaying descendants onto its parent.
pub fn delete_commit(repo_path: &str, target_sha: &str) -> Result<(), Box<dyn std::error::Error>> {
    println!("[GitService] Deleting commit {} from {}", target_sha, repo_path);
    let repo = Repository::open(repo_path)?;
    let target_oid = repo.revparse_single(target_sha)?.id();
    let target_commit = repo.find_commit(target_oid)?;

    if target_commit.parent_count() == 0 {
        return Err("无法删除初始存档（根节点）。".into());
    }
    let parent_oid = target_commit.parent_id(0)?;

    let head_ref = repo.head()?;
    let is_branch = head_ref.is_branch();
    let branch_name = if is_branch { head_ref.name().map(String::from) } else { None };
    let head_commit = head_ref.peel_to_commit()?;
    let head_oid = head_commit.id();

    // Fast path: deleting HEAD = reset to parent
    if head_oid == target_oid {
        println!("[GitService] Target is HEAD. Resetting to parent {}.", parent_oid.to_string()[..8].to_string());
        let parent_commit = repo.find_commit(parent_oid)?;
        repo.checkout_tree(parent_commit.as_object(), Some(git2::build::CheckoutBuilder::new().force()))?;

        // Update branch refs
        let branches = repo.branches(Some(git2::BranchType::Local))?;
        for br in branches {
            let (branch, _) = br?;
            if let Some(t) = branch.get().target() {
                if t == head_oid {
                    let rn = branch.get().name().unwrap_or("").to_string();
                    if !rn.is_empty() {
                        repo.reference(&rn, parent_oid, true, "Delete HEAD commit")?;
                    }
                }
            }
        }
        if let Some(ref_name) = branch_name {
            repo.set_head(&ref_name)?;
        } else {
            repo.set_head_detached(parent_oid)?;
        }
        println!("[GitService] HEAD commit deleted.");
        return Ok(());
    }

    // Historical: must be ancestor of HEAD
    if !repo.graph_descendant_of(head_oid, target_oid)? {
        return Err("该存档不是当前存档的直系祖先，无法安全删除。".into());
    }

    // Collect descendants (HEAD..target, exclusive of target)
    let mut revwalk = repo.revwalk()?;
    revwalk.push(head_oid)?;
    revwalk.hide(target_oid)?;
    revwalk.set_sorting(git2::Sort::TOPOLOGICAL | git2::Sort::REVERSE)?;
    let mut to_replay: Vec<git2::Oid> = Vec::new();
    for oid in revwalk { to_replay.push(oid?); }

    println!("[GitService] Replaying {} commits onto parent {}", to_replay.len(), parent_oid.to_string()[..8].to_string());

    // Checkout target's parent
    let parent_commit = repo.find_commit(parent_oid)?;
    repo.set_head_detached(parent_oid)?;
    repo.checkout_tree(parent_commit.as_object(), Some(git2::build::CheckoutBuilder::new().force()))?;

    let mut cur = parent_oid;
    for oid in to_replay {
        let c = repo.find_commit(oid)?;
        let p = repo.find_commit(cur)?;
        let mut idx = repo.cherrypick_commit(&c, &p, 0, None)
            .map_err(|e| format!("Cherry-pick failed on {}: {}", oid, e))?;
        if idx.has_conflicts() {
            return Err(format!("冲突: {}", oid).into());
        }
        let tree_oid = idx.write_tree_to(&repo)?;
        let tree = repo.find_tree(tree_oid)?;
        cur = repo.commit(Some("HEAD"), &c.author(), &c.committer(), c.message().unwrap_or(""), &tree, &[&p])?;
        let obj = repo.find_commit(cur)?;
        repo.checkout_tree(obj.as_object(), Some(git2::build::CheckoutBuilder::new().force()))?;
        println!("  -> Replayed: {}", oid.to_string()[..8].to_string());
    }

    // Update branch refs
    let branches = repo.branches(Some(git2::BranchType::Local))?;
    for br in branches {
        let (branch, _) = br?;
        if let Some(t) = branch.get().target() {
            if t == head_oid {
                let rn = branch.get().name().unwrap_or("").to_string();
                if !rn.is_empty() {
                    repo.reference(&rn, cur, true, "Delete commit: update branch")?;
                }
            }
        }
    }
    if let Some(ref_name) = branch_name {
        repo.set_head(&ref_name)?;
    } else {
        repo.set_head_detached(cur)?;
    }

    println!("[GitService] Commit deleted via rebase.");
    Ok(())
}
