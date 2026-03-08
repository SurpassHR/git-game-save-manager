// Config service — TOML-based config persistence with profile management
// See: /arch/adr-001-tauri-v2-migration.md

use std::fs;
use std::path::PathBuf;
use crate::models::config::{AppConfig, GameProfile};

/// Get the config file path under the OS config directory
fn config_path() -> PathBuf {
    let base = dirs::config_dir()
        .unwrap_or_else(|| PathBuf::from("."));
    let app_dir = base.join("git-game-save-manager");
    let _ = fs::create_dir_all(&app_dir);
    app_dir.join("config.toml")
}

/// Generate a short unique ID for profiles
fn generate_id() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis();
    format!("{:x}", ts)
}

/// Load config from TOML file, returning defaults if file doesn't exist
pub fn load_config() -> Result<AppConfig, Box<dyn std::error::Error>> {
    let path = config_path();
    if !path.exists() {
        return Ok(AppConfig::default());
    }
    let content = fs::read_to_string(&path)?;
    let mut config: AppConfig = toml::from_str(&content)?;

    // Migrate legacy repo_path → profile
    config.migrate_legacy();

    // Re-save to clean up legacy fields
    save_config(&config)?;

    Ok(config)
}

/// Save config to TOML file
pub fn save_config(config: &AppConfig) -> Result<(), Box<dyn std::error::Error>> {
    let path = config_path();
    let content = toml::to_string_pretty(config)?;
    fs::write(&path, content)?;
    Ok(())
}

/// Add a new game profile and return updated config
pub fn add_profile(name: &str, repo_path: &str, icon: &str) -> Result<AppConfig, Box<dyn std::error::Error>> {
    let mut config = load_config()?;
    let profile = GameProfile {
        id: generate_id(),
        name: name.to_string(),
        repo_path: repo_path.to_string(),
        icon: icon.to_string(),
    };
    let id = profile.id.clone();
    config.profiles.push(profile);

    // Auto-activate if it's the first profile
    if config.active_profile_id.is_empty() {
        config.active_profile_id = id;
    }

    save_config(&config)?;
    Ok(config)
}

/// Remove a game profile by ID and return updated config
pub fn remove_profile(id: &str) -> Result<AppConfig, Box<dyn std::error::Error>> {
    let mut config = load_config()?;
    config.profiles.retain(|p| p.id != id);

    // Reset active if we removed the active profile
    if config.active_profile_id == id {
        config.active_profile_id = config.profiles.first()
            .map(|p| p.id.clone())
            .unwrap_or_default();
    }

    save_config(&config)?;
    Ok(config)
}

/// Set the active profile by ID
pub fn set_active_profile(id: &str) -> Result<AppConfig, Box<dyn std::error::Error>> {
    let mut config = load_config()?;

    // Verify profile exists
    if !config.profiles.iter().any(|p| p.id == id) {
        return Err(format!("Profile '{}' not found", id).into());
    }

    config.active_profile_id = id.to_string();
    save_config(&config)?;
    Ok(config)
}
