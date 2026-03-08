// Git-related Tauri commands
// See: /arch/adr-001-tauri-v2-migration.md

use crate::models::commit::CommitInfo;
use crate::services::git_service;

/// List all commits in the repository at the given path
#[tauri::command]
pub fn list_commits(repo_path: &str) -> Result<Vec<CommitInfo>, String> {
    git_service::list_commits(repo_path).map_err(|e| e.to_string())
}

/// Get all branch names in the repository
#[tauri::command]
pub fn get_branches(repo_path: &str) -> Result<Vec<String>, String> {
    git_service::get_branches(repo_path).map_err(|e| e.to_string())
}

/// Initialize a git repository at the given path
#[tauri::command]
pub fn init_repo(repo_path: &str) -> Result<(), String> {
    git_service::init_repo(repo_path).map_err(|e| e.to_string())
}

/// Create a commit with all staged changes
#[tauri::command]
pub fn create_commit(repo_path: &str, message: &str) -> Result<String, String> {
    git_service::create_commit(repo_path, message).map_err(|e| e.to_string())
}

/// Checkout to a specific commit (detached HEAD)
#[tauri::command]
pub fn checkout_commit(repo_path: &str, commit_sha: &str) -> Result<(), String> {
    git_service::checkout_commit(repo_path, commit_sha).map_err(|e| e.to_string())
}

/// Hard reset to a specific commit
#[tauri::command]
pub fn reset_hard_commit(repo_path: &str, commit_sha: &str) -> Result<(), String> {
    git_service::reset_hard_commit(repo_path, commit_sha).map_err(|e| e.to_string())
}

/// Amend current commit message
#[tauri::command]
pub fn amend_commit(repo_path: &str, new_message: &str) -> Result<String, String> {
    git_service::amend_commit(repo_path, new_message).map_err(|e| e.to_string())
}
