// Zustand store for application state
// See: /arch/adr-001-tauri-v2-migration.md

import { create } from "zustand";
import type { CommitInfo, AppConfig } from "../types";
import * as gitService from "../services/gitService";
import * as configService from "../services/configService";

interface AppState {
    // Config
    config: AppConfig;
    setConfig: (config: AppConfig) => void;
    loadConfig: () => Promise<void>;
    saveConfig: (config: Partial<AppConfig>) => Promise<void>;

    // Commits
    commits: CommitInfo[];
    setCommits: (commits: CommitInfo[]) => void;
    loadCommits: () => Promise<void>;

    // Branches
    branches: string[];
    setBranches: (branches: string[]) => void;

    // UI state
    selectedCommit: string | null;
    setSelectedCommit: (sha: string | null) => void;
    currentPage: "config" | "graph";
    setCurrentPage: (page: "config" | "graph") => void;

    // Loading / Error
    loading: boolean;
    error: string | null;
    setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
    // Config
    config: { theme: "dark", repo_path: "" },
    setConfig: (config) => set({ config }),

    loadConfig: async () => {
        try {
            const config = await configService.getConfig();
            set({ config });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    saveConfig: async (partial) => {
        const current = get().config;
        const updated = { ...current, ...partial };
        try {
            await configService.setConfig(updated);
            set({ config: updated, error: null });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    // Commits
    commits: [],
    setCommits: (commits) => set({ commits }),

    loadCommits: async () => {
        const repoPath = get().config.repo_path;
        if (!repoPath) return;
        set({ loading: true, error: null });
        try {
            const [commits, branches] = await Promise.all([
                gitService.listCommits(repoPath),
                gitService.getBranches(repoPath),
            ]);
            set({ commits, branches, loading: false });
        } catch (e) {
            set({ loading: false, error: String(e) });
        }
    },

    // Branches
    branches: [],
    setBranches: (branches) => set({ branches }),

    // UI state
    selectedCommit: null,
    setSelectedCommit: (sha) => set({ selectedCommit: sha }),
    currentPage: "config",
    setCurrentPage: (page) => set({ currentPage: page }),

    // Loading / Error
    loading: false,
    error: null,
    setError: (error) => set({ error }),
}));
