// Config IPC service — wraps @tauri-apps/api invoke calls
// See: /arch/adr-001-tauri-v2-migration.md

import { invoke } from "@tauri-apps/api/core";
import type { AppConfig } from "../types";

/**
 * Load application config from Rust backend
 */
export async function getConfig(): Promise<AppConfig> {
    return invoke<AppConfig>("get_config");
}

/**
 * Save application config via Rust backend
 */
export async function setConfig(config: AppConfig): Promise<void> {
    return invoke<void>("set_config", { config });
}
