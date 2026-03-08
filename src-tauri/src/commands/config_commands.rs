// Config-related Tauri commands
// See: /arch/adr-001-tauri-v2-migration.md

use crate::models::config::AppConfig;
use crate::services::config_service;

/// Get the current application config
#[tauri::command]
pub fn get_config() -> Result<AppConfig, String> {
    config_service::load_config().map_err(|e| e.to_string())
}

/// Update the full config
#[tauri::command]
pub fn set_config(config: AppConfig) -> Result<(), String> {
    config_service::save_config(&config).map_err(|e| e.to_string())
}

/// Add a new game profile
#[tauri::command]
pub fn add_profile(name: String, repo_path: String, icon: String) -> Result<AppConfig, String> {
    config_service::add_profile(&name, &repo_path, &icon).map_err(|e| e.to_string())
}

/// Remove a game profile by ID
#[tauri::command]
pub fn remove_profile(id: String) -> Result<AppConfig, String> {
    config_service::remove_profile(&id).map_err(|e| e.to_string())
}

/// Set the active profile by ID
#[tauri::command]
pub fn set_active_profile(id: String) -> Result<AppConfig, String> {
    config_service::set_active_profile(&id).map_err(|e| e.to_string())
}
