pub mod commands;
pub mod models;
pub mod services;

use commands::git_commands::*;
use commands::config_commands::*;

// See: /walkthrough/refactor-plan-tauri-v2-migration.md

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            // Git commands
            list_commits,
            get_branches,
            init_repo,
            create_commit,
            checkout_commit,
            // Config commands
            get_config,
            set_config,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
