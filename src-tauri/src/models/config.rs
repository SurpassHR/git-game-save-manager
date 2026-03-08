use serde::{Deserialize, Serialize};

/// A single game save profile
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameProfile {
    pub id: String,
    pub name: String,
    pub repo_path: String,
    pub icon: String,
}

/// Application configuration persisted as TOML
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    /// Current theme: "light" or "dark"
    pub theme: String,
    /// ID of the currently active game profile
    pub active_profile_id: String,
    /// List of game save profiles
    pub profiles: Vec<GameProfile>,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            theme: "dark".to_string(),
            active_profile_id: String::new(),
            profiles: Vec::new(),
        }
    }
}

impl AppConfig {
    /// Get the currently active profile, if any
    pub fn active_profile(&self) -> Option<&GameProfile> {
        self.profiles.iter().find(|p| p.id == self.active_profile_id)
    }
}
