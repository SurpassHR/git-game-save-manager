// Config Page — select save directory
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import { open } from "@tauri-apps/plugin-dialog";
import { useAppStore } from "../store";
import * as gitService from "../services/gitService";

export function ConfigPage() {
    const { config, saveConfig, error, setError } = useAppStore();

    const handleSelectFolder = async () => {
        try {
            const selected = await open({
                directory: true,
                multiple: false,
                title: "选择存档目录",
            });
            if (selected) {
                await saveConfig({ repo_path: selected as string });
            }
        } catch (e) {
            setError(String(e));
        }
    };

    const handleInitRepo = async () => {
        if (!config.repo_path) return;
        try {
            await gitService.initRepo(config.repo_path);
            setError(null);
            // Reload commits after init
            useAppStore.getState().loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    return (
        <div className="page">
            <h2 className="page-title">配置管理</h2>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {/* Select Repo Card */}
            <div className="card">
                <div className="card-title">存档目录</div>
                <div className="card-description">
                    选择游戏存档所在的目录，将使用 Git 进行版本管理
                </div>

                {config.repo_path ? (
                    <div className="repo-path">
                        <span>📁</span>
                        <span className="path-value">{config.repo_path}</span>
                    </div>
                ) : (
                    <div className="repo-path">
                        <span>📁</span>
                        <span className="path-value" style={{ color: "var(--text-muted)" }}>
                            未选择目录
                        </span>
                    </div>
                )}

                <div className="toolbar" style={{ marginTop: 16 }}>
                    <button className="btn btn-primary" onClick={handleSelectFolder}>
                        📂 选择文件夹
                    </button>
                    {config.repo_path && (
                        <button className="btn" onClick={handleInitRepo}>
                            🔧 初始化仓库
                        </button>
                    )}
                </div>
            </div>

            {/* Theme Card */}
            <div className="card">
                <div className="card-title">主题设置</div>
                <div className="card-description">当前主题: {config.theme}</div>
                <button
                    className="btn"
                    onClick={() =>
                        saveConfig({
                            theme: config.theme === "dark" ? "light" : "dark",
                        })
                    }
                >
                    🎨 切换主题
                </button>
            </div>
        </div>
    );
}
