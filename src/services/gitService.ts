// Tauri IPC service — wraps @tauri-apps/api invoke calls
// See: /arch/adr-001-tauri-v2-migration.md

import { invoke } from "@tauri-apps/api/core";
import type { CommitInfo } from "../types";

/**
 * List all commits in the given repository
 */
export async function listCommits(repoPath: string): Promise<CommitInfo[]> {
    return invoke<CommitInfo[]>("list_commits", { repoPath });
}

/**
 * Get all branch names in the repository
 */
export async function getBranches(repoPath: string): Promise<string[]> {
    return invoke<string[]>("get_branches", { repoPath });
}

/**
 * Initialize a git repository at the given path
 */
export async function initRepo(repoPath: string): Promise<void> {
    return invoke<void>("init_repo", { repoPath });
}

/**
 * Create a commit with all current changes
 */
export async function createCommit(
    repoPath: string,
    message: string
): Promise<string> {
    return invoke<string>("create_commit", { repoPath, message });
}

/**
 * Checkout to a specific commit (detached HEAD)
 */
export async function checkoutCommit(
    repoPath: string,
    commitSha: string
): Promise<void> {
    return invoke<void>("checkout_commit", { repoPath, commitSha });
}

/**
 * Hard reset to a specific commit (discards all later detached history)
 */
export async function resetHard(
    repoPath: string,
    commitSha: string
): Promise<void> {
    return invoke<void>("reset_hard_commit", { repoPath, commitSha });
}

/**
 * Amend the message of the current HEAD commit
 */
export async function amendCommit(
    repoPath: string,
    newMessage: string
): Promise<string> {
    return invoke<string>("amend_commit", { repoPath, newMessage });
}
