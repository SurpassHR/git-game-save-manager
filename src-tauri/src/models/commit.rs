use serde::{Deserialize, Serialize};

/// Represents a single git commit's metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CommitInfo {
    pub hex_sha: String,
    pub author: String,
    pub message: String,
    pub parents: Vec<String>,
    pub branches: Vec<String>,
    pub timestamp: i64,
}

/// Represents a branch with its head commit
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BranchInfo {
    pub name: String,
    pub head_sha: String,
    pub is_current: bool,
}
