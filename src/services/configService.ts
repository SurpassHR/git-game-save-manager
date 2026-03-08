// Config IPC service — wraps @tauri-apps/api invoke calls
// See: /arch/adr-001-tauri-v2-migration.md

import { invoke } from "@tauri-apps/api/core";
import type { AppConfig } from "../types";

export async function getConfig(): Promise<AppConfig> {
    return invoke<AppConfig>("get_config");
}

export async function setConfig(config: AppConfig): Promise<void> {
    return invoke<void>("set_config", { config });
}

export async function addProfile(
    name: string,
    repoPath: string,
    icon: string
): Promise<AppConfig> {
    return invoke<AppConfig>("add_profile", { name, repoPath, icon });
}

export async function removeProfile(id: string): Promise<AppConfig> {
    return invoke<AppConfig>("remove_profile", { id });
}

export async function setActiveProfile(id: string): Promise<AppConfig> {
    return invoke<AppConfig>("set_active_profile", { id });
}
