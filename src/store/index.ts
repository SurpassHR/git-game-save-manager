// Zustand store for application state
// See: /arch/adr-001-tauri-v2-migration.md

import { create } from "zustand";
import type { CommitInfo, AppConfig, GameProfile } from "../types";
import * as gitService from "../services/gitService";
import * as configService from "../services/configService";

interface AppState {
    // Config
    config: AppConfig;
    setConfig: (config: AppConfig) => void;
    loadConfig: () => Promise<void>;
    saveConfig: (config: AppConfig) => Promise<void>;

    // Profile helpers
    activeProfile: GameProfile | null;
    addProfile: (name: string, repoPath: string, icon: string) => Promise<void>;
    removeProfile: (id: string) => Promise<void>;
    switchProfile: (id: string) => Promise<void>;
    setTheme: (theme: "light" | "dark") => Promise<void>;

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

function getActiveProfile(config: AppConfig): GameProfile | null {
    return (
        config.profiles.find((p) => p.id === config.active_profile_id) ?? null
    );
}

export const useAppStore = create<AppState>((set, get) => ({
    // Config
    config: { theme: "dark", active_profile_id: "", profiles: [] },
    setConfig: (config) =>
        set({ config, activeProfile: getActiveProfile(config) }),

    loadConfig: async () => {
        try {
            const config = await configService.getConfig();
            set({ config, activeProfile: getActiveProfile(config) });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    saveConfig: async (config) => {
        try {
            await configService.setConfig(config);
            set({ config, activeProfile: getActiveProfile(config), error: null });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    // Profile helpers
    activeProfile: null,

    addProfile: async (name, repoPath, icon) => {
        try {
            const config = await configService.addProfile(name, repoPath, icon);
            set({ config, activeProfile: getActiveProfile(config), error: null });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    removeProfile: async (id) => {
        try {
            const config = await configService.removeProfile(id);
            set({
                config,
                activeProfile: getActiveProfile(config),
                error: null,
                commits: [],
                branches: [],
            });
        } catch (e) {
            set({ error: String(e) });
        }
    },

    switchProfile: async (id) => {
        try {
            const config = await configService.setActiveProfile(id);
            set({
                config,
                activeProfile: getActiveProfile(config),
                error: null,
                commits: [],
                branches: [],
                selectedCommit: null,
            });
            // Re-load commits for new profile
            get().loadCommits();
        } catch (e) {
            set({ error: String(e) });
        }
    },

    setTheme: async (theme) => {
        const current = get().config;
        const updated = { ...current, theme };
        try {
            await configService.setConfig(updated);
            set({ config: updated, error: null });
            document.documentElement.dataset.theme = theme;
        } catch (e) {
            set({ error: String(e) });
        }
    },

    // Commits
    commits: [],
    setCommits: (commits) => set({ commits }),

    loadCommits: async () => {
        const profile = get().activeProfile;
        if (!profile) return;
        set({ loading: true, error: null });
        try {
            const [commits, branches] = await Promise.all([
                gitService.listCommits(profile.repo_path),
                gitService.getBranches(profile.repo_path),
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
