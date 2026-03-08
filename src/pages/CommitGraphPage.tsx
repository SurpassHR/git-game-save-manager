// Commit Graph Page — displays commit history
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import { useEffect, useState } from "react";
import { useAppStore } from "../store";
import * as gitService from "../services/gitService";

export function CommitGraphPage() {
    const {
        commits,
        branches,
        loading,
        error,
        loadCommits,
        config,
        selectedCommit,
        setSelectedCommit,
        setError,
        setCurrentPage,
    } = useAppStore();

    const [commitMessage, setCommitMessage] = useState("");

    useEffect(() => {
        if (config.repo_path) {
            loadCommits();
        }
    }, [config.repo_path]);

    const handleCreateCommit = async () => {
        if (!config.repo_path || !commitMessage.trim()) return;
        try {
            await gitService.createCommit(config.repo_path, commitMessage.trim());
            setCommitMessage("");
            loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    const handleCheckout = async (sha: string) => {
        if (!config.repo_path) return;
        try {
            await gitService.checkoutCommit(config.repo_path, sha);
            loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    const formatTime = (ts: number) => {
        return new Date(ts * 1000).toLocaleString("zh-CN", {
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    // No repo configured
    if (!config.repo_path) {
        return (
            <div className="page">
                <div className="empty-state">
                    <div className="empty-icon">📂</div>
                    <div className="empty-text">尚未配置存档目录</div>
                    <div className="empty-hint">请先在配置管理中选择存档目录</div>
                    <button
                        className="btn btn-primary"
                        style={{ marginTop: 16 }}
                        onClick={() => setCurrentPage("config")}
                    >
                        前往配置
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="page" style={{ maxWidth: "100%" }}>
            <h2 className="page-title">存档视图</h2>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {/* Toolbar */}
            <div className="toolbar">
                <input
                    className="input"
                    style={{ maxWidth: 300 }}
                    placeholder="存档说明..."
                    value={commitMessage}
                    onChange={(e) => setCommitMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleCreateCommit()}
                />
                <button
                    className="btn btn-success"
                    onClick={handleCreateCommit}
                    disabled={!commitMessage.trim()}
                >
                    💾 保存存档
                </button>
                <button className="btn" onClick={() => loadCommits()}>
                    🔄 刷新
                </button>

                {selectedCommit && (
                    <button
                        className="btn btn-primary"
                        onClick={() => handleCheckout(selectedCommit)}
                    >
                        ⏪ 恢复到此存档
                    </button>
                )}
            </div>

            {/* Branch Info */}
            {branches.length > 0 && (
                <div className="toolbar">
                    {branches.map((b) => (
                        <span key={b} className="branch-tag">
                            {b}
                        </span>
                    ))}
                </div>
            )}

            {/* Loading */}
            {loading && <div className="loading-spinner">加载中...</div>}

            {/* Commit List */}
            {!loading && commits.length === 0 && (
                <div className="empty-state">
                    <div className="empty-icon">📝</div>
                    <div className="empty-text">暂无存档记录</div>
                    <div className="empty-hint">
                        输入说明并点击"保存存档"创建第一个存档
                    </div>
                </div>
            )}

            {!loading && commits.length > 0 && (
                <div className="commit-list">
                    {commits.map((commit) => (
                        <div
                            key={commit.hex_sha}
                            className={`commit-item ${selectedCommit === commit.hex_sha ? "selected" : ""
                                }`}
                            onClick={() =>
                                setSelectedCommit(
                                    selectedCommit === commit.hex_sha ? null : commit.hex_sha
                                )
                            }
                        >
                            <span className="commit-sha">{commit.hex_sha}</span>
                            <div>
                                <div className="commit-message">{commit.message}</div>
                                <div className="commit-meta">
                                    <span>{commit.author}</span>
                                    <span>·</span>
                                    <span>{formatTime(commit.timestamp)}</span>
                                    {commit.branches.map((b) => (
                                        <span key={b} className="branch-tag">
                                            {b}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div className="commit-meta">
                                {commit.parents.length > 0 && (
                                    <span>← {commit.parents.join(", ")}</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
