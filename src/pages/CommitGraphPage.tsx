// Commit Graph Page — React Flow DAG visualization
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import { useCallback, useEffect, useState } from "react";
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    BackgroundVariant,
    useNodesState,
    useEdgesState,
    type NodeMouseHandler,
    type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useAppStore } from "../store";
import { useCommitGraph } from "../hooks/useCommitGraph";
import { CommitNode } from "../components/CommitNode";
import { CommitDetailPanel } from "../components/CommitDetailPanel";
import { resetHard, amendCommit, deleteCommit } from "../services/gitService";
import * as gitService from "../services/gitService";
import { ask, message } from "@tauri-apps/plugin-dialog";
import { ContextMenu } from "../components/ContextMenu";

const nodeTypes = { commitNode: CommitNode };

export function CommitGraphPage() {
    const {
        commits,
        branches,
        loading,
        error,
        loadCommits,
        activeProfile,
        selectedCommit,
        setSelectedCommit,
        setError,
        setCurrentPage,
    } = useAppStore();

    const [commitMessage, setCommitMessage] = useState("");

    // Context Menu State
    const [contextMenu, setContextMenu] = useState<{
        x: number;
        y: number;
        commitSha: string;
    } | null>(null);

    // Prompt Modal State for amending messages
    const [promptModal, setPromptModal] = useState<{
        isOpen: boolean;
        sha: string;
        currentMessage: string;
    }>({ isOpen: false, sha: "", currentMessage: "" });

    // Find selected commit data
    const selectedCommitData = commits.find(
        (c) => c.hex_sha === selectedCommit
    );

    // Convert commits to React Flow data
    const { nodes: layoutNodes, edges: layoutEdges } = useCommitGraph(
        commits,
        selectedCommit
    );
    const [nodes, setNodes, onNodesChange] = useNodesState(layoutNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(layoutEdges);

    // Sync layout data when commits change
    useEffect(() => {
        setNodes(layoutNodes);
        setEdges(layoutEdges);
    }, [layoutNodes, layoutEdges]);

    useEffect(() => {
        if (activeProfile) {
            loadCommits();
        }
    }, [activeProfile]);

    const handleCreateCommit = async () => {
        if (!activeProfile || !commitMessage.trim()) return;
        try {
            await gitService.createCommit(
                activeProfile.repo_path,
                commitMessage.trim()
            );
            setCommitMessage("");
            loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    const handleCheckout = async (sha: string) => {
        if (!activeProfile) return;
        try {
            await gitService.checkoutCommit(activeProfile.repo_path, sha);
            setSelectedCommit(null);
            loadCommits();
        } catch (e) {
            setError(String(e));
        }
    };

    const onNodeClick: NodeMouseHandler = useCallback(
        (_, node) => {
            setSelectedCommit(selectedCommit === node.id ? null : node.id);
        },
        [selectedCommit, setSelectedCommit]
    );

    const onNodeContextMenu = useCallback(
        (event: React.MouseEvent, node: Node) => {
            event.preventDefault();
            const d = node.data as { hexSha: string };
            setContextMenu({
                x: event.clientX,
                y: event.clientY,
                commitSha: d.hexSha,
            });
        },
        []
    );

    const handleResetHard = async (sha: string) => {
        if (!activeProfile) return;
        const confirmed = await ask(
            `警告：这将恢复到存档 ${sha}，并且丢弃此后产生的所有未来存档和未提交数据。确定要继续吗？`,
            { title: "恢复存档并切除未来", kind: "warning" }
        );
        if (confirmed) {
            try {
                await resetHard(activeProfile.repo_path, sha);
                await loadCommits();
            } catch (err) {
                console.error("Failed to reset hard:", err);
            }
        }
    };

    const handleDeleteCommit = async (sha: string) => {
        if (!activeProfile) return;
        const confirmed = await ask(
            `警告：这将从历史中永久删除存档 ${sha}，此操作不可逆。确定要继续吗？`,
            { title: "删除存档", kind: "warning" }
        );
        if (confirmed) {
            try {
                await deleteCommit(activeProfile.repo_path, sha);
                await loadCommits();
            } catch (err) {
                console.error("Failed to delete commit:", err);
                await message(String(err), { title: "删除存档失败", kind: "error" });
            }
        }
    };

    const handleAmendMessage = (sha: string) => {
        if (!activeProfile) return;
        const currentMessage = commits.find((c) => c.hex_sha === sha)?.message || "";
        setPromptModal({ isOpen: true, sha, currentMessage });
    };

    const handlePromptConfirm = async (newMessage: string) => {
        const { sha, currentMessage } = promptModal;
        setPromptModal((p) => ({ ...p, isOpen: false }));

        console.log("[Amend Debug] sha:", sha);
        console.log("[Amend Debug] newMessage:", JSON.stringify(newMessage));
        console.log("[Amend Debug] currentMessage:", JSON.stringify(currentMessage));
        console.log("[Amend Debug] activeProfile:", !!activeProfile);
        console.log("[Amend Debug] condition:", newMessage && newMessage !== currentMessage && !!activeProfile);

        if (newMessage && newMessage !== currentMessage && activeProfile) {
            try {
                console.log("[Amend Debug] Calling amendCommit...");
                await amendCommit(activeProfile.repo_path, sha, newMessage);
                console.log("[Amend Debug] amendCommit returned. Calling loadCommits...");
                await loadCommits();
                console.log("[Amend Debug] loadCommits returned.");
            } catch (err) {
                console.error("Failed to amend commit:", err);
                await message(String(err), { title: "修改说明失败", kind: "error" });
            }
        } else {
            console.warn("[Amend Debug] Skipped! Condition was false.");
        }
    };

    // No profile configured
    if (!activeProfile) {
        return (
            <div className="page">
                <div className="empty-state">
                    <div className="empty-icon">📂</div>
                    <div className="empty-text">尚未配置游戏存档</div>
                    <div className="empty-hint">请先在配置管理中添加游戏</div>
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
        <div className="graph-page">
            {error && (
                <div className="error-banner" style={{ margin: "12px 16px 0" }}>
                    ⚠️ {error}
                </div>
            )}

            {/* Toolbar */}
            <div className="graph-toolbar">
                <span className="graph-toolbar__game">
                    {activeProfile.icon} {activeProfile.name}
                </span>
                <div className="graph-toolbar__separator" />
                <input
                    className="input"
                    style={{ maxWidth: 280 }}
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

                {/* Branch tags */}
                <div className="graph-toolbar__branches">
                    {branches.map((b) => (
                        <span key={b} className="branch-tag">
                            {b}
                        </span>
                    ))}
                </div>
            </div>

            {/* Loading */}
            {loading && <div className="loading-spinner">加载中...</div>}

            {/* Empty */}
            {!loading && commits.length === 0 && (
                <div className="empty-state">
                    <div className="empty-icon">📝</div>
                    <div className="empty-text">暂无存档记录</div>
                    <div className="empty-hint">
                        输入说明并点击"保存存档"创建第一个存档
                    </div>
                </div>
            )}

            {/* Context Menu Overlay */}
            {contextMenu && (
                <ContextMenu
                    x={contextMenu.x}
                    y={contextMenu.y}
                    commitSha={contextMenu.commitSha}
                    onClose={() => setContextMenu(null)}
                    onResetHard={handleResetHard}
                    onDeleteCommit={handleDeleteCommit}
                    onAmendMessage={handleAmendMessage}
                />
            )}

            {/* Prompt Modal Overlay */}
            <PromptModal
                isOpen={promptModal.isOpen}
                title="修改存档说明"
                defaultValue={promptModal.currentMessage}
                onConfirm={handlePromptConfirm}
                onCancel={() => setPromptModal((p) => ({ ...p, isOpen: false }))}
            />

            {/* React Flow DAG + Detail Panel */}
            {!loading && commits.length > 0 && (
                <div className="graph-main">
                    <div className="graph-container">
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            onNodeClick={onNodeClick}
                            onNodeContextMenu={onNodeContextMenu}
                            onPaneClick={() => setContextMenu(null)}
                            nodeTypes={nodeTypes}
                            fitView
                            fitViewOptions={{ padding: 0.3 }}
                            minZoom={0.2}
                            maxZoom={2}
                            defaultEdgeOptions={{
                                type: "smoothstep",
                                style: { stroke: "var(--accent)", strokeWidth: 2 },
                            }}
                            proOptions={{ hideAttribution: true }}
                            onlyRenderVisibleElements={true}
                        >
                            <Background
                                variant={BackgroundVariant.Dots}
                                gap={20}
                                size={1}
                                color="var(--border-subtle)"
                            />
                            <Controls showInteractive={false} position="bottom-right" />
                            <MiniMap
                                nodeStrokeColor="var(--accent)"
                                nodeColor="var(--bg-tertiary)"
                                maskColor="rgba(0, 0, 0, 0.6)"
                                style={{ background: "var(--bg-secondary)" }}
                            />
                        </ReactFlow>
                    </div>

                    {/* Detail Panel */}
                    {selectedCommitData && (
                        <CommitDetailPanel
                            commit={selectedCommitData}
                            onCheckout={handleCheckout}
                            onClose={() => setSelectedCommit(null)}
                        />
                    )}
                </div>
            )}
        </div>
    );
}

// React modal component for requesting user text input safely in Tauri
function PromptModal({
    isOpen,
    title,
    defaultValue,
    onConfirm,
    onCancel,
}: {
    isOpen: boolean;
    title: string;
    defaultValue: string;
    onConfirm: (val: string) => void;
    onCancel: () => void;
}) {
    const [val, setVal] = useState(defaultValue);

    useEffect(() => {
        setVal(defaultValue);
    }, [defaultValue, isOpen]);

    // Handle escape globally when open
    useEffect(() => {
        if (!isOpen) return;
        const handleKd = (e: KeyboardEvent) => e.key === "Escape" && onCancel();
        document.addEventListener("keydown", handleKd);
        return () => document.removeEventListener("keydown", handleKd);
    }, [isOpen, onCancel]);

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>{title}</h3>
                <input
                    className="input"
                    value={val}
                    onChange={(e) => setVal(e.target.value)}
                    autoFocus
                    style={{ width: "100%", marginBottom: "16px" }}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") onConfirm(val);
                        // Escape gives way to the global event listener above
                    }}
                />
                <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                    <button className="btn" onClick={onCancel}>取消</button>
                    <button className="btn btn-primary" onClick={() => onConfirm(val)}>确认</button>
                </div>
            </div>
        </div>
    );
}
