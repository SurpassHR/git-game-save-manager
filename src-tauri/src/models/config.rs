use serde::{Deserialize, Serialize};

/// Application configuration persisted as TOML
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    /// Current theme: "light" or "dark"
    pub theme: String,
    /// Path to the currently managed game save repository
    pub repo_path: String,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            theme: "dark".to_string(),
            repo_path: String::new(),
        }
    }
}
