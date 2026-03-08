// TypeScript type definitions matching Rust models
// See: /arch/adr-001-tauri-v2-migration.md

/** Matches `CommitInfo` in src-tauri/src/models/commit.rs */
export interface CommitInfo {
    hex_sha: string;
    author: string;
    message: string;
    parents: string[];
    branches: string[];
    timestamp: number;
    is_current: boolean;
}

/** Matches `BranchInfo` in src-tauri/src/models/commit.rs */
export interface BranchInfo {
    name: string;
    head_sha: string;
    is_current: boolean;
}

/** Matches `GameProfile` in src-tauri/src/models/config.rs */
export interface GameProfile {
    id: string;
    name: string;
    repo_path: string;
    icon: string;
}

/** Matches `AppConfig` in src-tauri/src/models/config.rs */
export interface AppConfig {
    theme: "light" | "dark";
    active_profile_id: string;
    profiles: GameProfile[];
}
