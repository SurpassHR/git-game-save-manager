// Config-related Tauri commands
// See: /arch/adr-001-tauri-v2-migration.md

use crate::models::config::AppConfig;
use crate::services::config_service;

/// Get the current application config
#[tauri::command]
pub fn get_config() -> Result<AppConfig, String> {
    config_service::load_config().map_err(|e| e.to_string())
}

/// Update a config field
#[tauri::command]
pub fn set_config(config: AppConfig) -> Result<(), String> {
    config_service::save_config(&config).map_err(|e| e.to_string())
}
