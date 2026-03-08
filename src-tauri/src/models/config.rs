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
#[serde(default)]
pub struct AppConfig {
    /// Current theme: "light" or "dark"
    pub theme: String,
    /// ID of the currently active game profile
    pub active_profile_id: String,
    /// List of game save profiles
    pub profiles: Vec<GameProfile>,
    /// Legacy field — auto-migrated to a profile on load
    #[serde(skip_serializing)]
    repo_path: Option<String>,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            theme: "dark".to_string(),
            active_profile_id: String::new(),
            profiles: Vec::new(),
            repo_path: None,
        }
    }
}

impl AppConfig {
    /// Get the currently active profile, if any
    pub fn active_profile(&self) -> Option<&GameProfile> {
        self.profiles.iter().find(|p| p.id == self.active_profile_id)
    }

    /// Migrate legacy repo_path field into a profile
    pub fn migrate_legacy(&mut self) {
        if let Some(path) = self.repo_path.take() {
            if !path.is_empty() && self.profiles.is_empty() {
                let profile = GameProfile {
                    id: "legacy".to_string(),
                    name: "游戏存档".to_string(),
                    repo_path: path,
                    icon: "🎮".to_string(),
                };
                self.active_profile_id = profile.id.clone();
                self.profiles.push(profile);
            }
        }
    }
}
