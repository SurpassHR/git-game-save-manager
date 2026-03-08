// Config service — TOML-based config persistence
// See: /arch/adr-001-tauri-v2-migration.md

use std::fs;
use std::path::PathBuf;
use crate::models::config::AppConfig;

/// Get the config file path under the OS config directory
fn config_path() -> PathBuf {
    let base = dirs::config_dir()
        .unwrap_or_else(|| PathBuf::from("."));
    let app_dir = base.join("git-game-save-manager");
    // Ensure directory exists
    let _ = fs::create_dir_all(&app_dir);
    app_dir.join("config.toml")
}

/// Load config from TOML file, returning defaults if file doesn't exist
pub fn load_config() -> Result<AppConfig, Box<dyn std::error::Error>> {
    let path = config_path();
    if !path.exists() {
        return Ok(AppConfig::default());
    }
    let content = fs::read_to_string(&path)?;
    let config: AppConfig = toml::from_str(&content)?;
    Ok(config)
}

/// Save config to TOML file
pub fn save_config(config: &AppConfig) -> Result<(), Box<dyn std::error::Error>> {
    let path = config_path();
    let content = toml::to_string_pretty(config)?;
    fs::write(&path, content)?;
    Ok(())
}
