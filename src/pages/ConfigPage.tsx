// Config Page — multi-game profile management
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import { useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { useAppStore } from "../store";
import * as gitService from "../services/gitService";

const GAME_ICONS = ["🎮", "🕹️", "🎲", "🏰", "⚔️", "🚀", "🐉", "🌟", "🎯", "🔮"];

export function ConfigPage() {
    const {
        config,
        activeProfile,
        addProfile,
        removeProfile,
        error,
        setError,
    } = useAppStore();

    const [newName, setNewName] = useState("");
    const [newPath, setNewPath] = useState("");
    const [newIcon, setNewIcon] = useState("🎮");
    const [showAddForm, setShowAddForm] = useState(false);

    const handleSelectFolder = async () => {
        try {
            const selected = await open({
                directory: true,
                multiple: false,
                title: "选择存档目录",
            });
            if (selected) {
                setNewPath(selected as string);
            }
        } catch (e) {
            setError(String(e));
        }
    };

    const handleAddProfile = async () => {
        if (!newName.trim() || !newPath.trim()) return;
        await addProfile(newName.trim(), newPath.trim(), newIcon);
        setNewName("");
        setNewPath("");
        setNewIcon("🎮");
        setShowAddForm(false);
    };

    const handleInitRepo = async () => {
        if (!activeProfile) return;
        try {
            await gitService.initRepo(activeProfile.repo_path);
            setError(null);
            useAppStore.getState().loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    return (
        <div className="page">
            <h2 className="page-title">配置管理</h2>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {/* Game Profiles Card */}
            <div className="card">
                <div className="card-header">
                    <div className="card-title">游戏配置</div>
                    <button
                        className="btn btn-primary btn-sm"
                        onClick={() => setShowAddForm(!showAddForm)}
                    >
                        {showAddForm ? "✕ 取消" : "＋ 添加游戏"}
                    </button>
                </div>
                <div className="card-description">
                    管理多个游戏的存档目录，每个游戏独立版本管理
                </div>

                {/* Add Profile Form */}
                {showAddForm && (
                    <div className="add-profile-form">
                        <div className="form-row">
                            <div className="icon-picker">
                                {GAME_ICONS.map((icon) => (
                                    <button
                                        key={icon}
                                        className={`icon-btn ${newIcon === icon ? "active" : ""}`}
                                        onClick={() => setNewIcon(icon)}
                                    >
                                        {icon}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="form-row">
                            <input
                                className="input"
                                placeholder="游戏名称"
                                value={newName}
                                onChange={(e) => setNewName(e.target.value)}
                            />
                        </div>
                        <div className="form-row">
                            <div className="path-input-group">
                                <input
                                    className="input"
                                    placeholder="存档目录路径"
                                    value={newPath}
                                    readOnly
                                />
                                <button className="btn" onClick={handleSelectFolder}>
                                    📂 选择
                                </button>
                            </div>
                        </div>
                        <button
                            className="btn btn-success"
                            onClick={handleAddProfile}
                            disabled={!newName.trim() || !newPath.trim()}
                        >
                            ✓ 确认添加
                        </button>
                    </div>
                )}

                {/* Profile List */}
                {config.profiles.length === 0 && !showAddForm && (
                    <div className="empty-state" style={{ padding: "30px 0" }}>
                        <div className="empty-icon">🎮</div>
                        <div className="empty-text">暂无游戏配置</div>
                        <div className="empty-hint">点击"添加游戏"开始管理存档</div>
                    </div>
                )}

                <div className="profile-list">
                    {config.profiles.map((profile) => (
                        <div
                            key={profile.id}
                            className={`profile-item ${config.active_profile_id === profile.id
                                    ? "profile-item--active"
                                    : ""
                                }`}
                        >
                            <span className="profile-icon">{profile.icon}</span>
                            <div className="profile-info">
                                <div className="profile-name">{profile.name}</div>
                                <div className="profile-path">{profile.repo_path}</div>
                            </div>
                            <button
                                className="btn btn-sm btn-danger"
                                onClick={() => removeProfile(profile.id)}
                            >
                                🗑️
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Active Profile Actions */}
            {activeProfile && (
                <div className="card">
                    <div className="card-title">
                        {activeProfile.icon} {activeProfile.name} — 仓库操作
                    </div>
                    <div className="repo-path">
                        <span>📁</span>
                        <span className="path-value">{activeProfile.repo_path}</span>
                    </div>
                    <div className="toolbar" style={{ marginTop: 12 }}>
                        <button className="btn" onClick={handleInitRepo}>
                            🔧 初始化仓库
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
