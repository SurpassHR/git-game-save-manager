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
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useAppStore } from "../store";
import { useCommitGraph } from "../hooks/useCommitGraph";
import { CommitNode } from "../components/CommitNode";
import * as gitService from "../services/gitService";

const nodeTypes = { commitNode: CommitNode };

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

    const onNodeClick: NodeMouseHandler = useCallback(
        (_, node) => {
            setSelectedCommit(
                selectedCommit === node.id ? null : node.id
            );
        },
        [selectedCommit, setSelectedCommit]
    );

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
        <div className="graph-page">
            {error && <div className="error-banner" style={{ margin: "12px 16px 0" }}>⚠️ {error}</div>}

            {/* Toolbar */}
            <div className="graph-toolbar">
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

                {selectedCommit && (
                    <button
                        className="btn btn-primary"
                        onClick={() => handleCheckout(selectedCommit)}
                    >
                        ⏪ 恢复到 {selectedCommit}
                    </button>
                )}

                {/* Branch tags */}
                <div className="graph-toolbar__branches">
                    {branches.map((b) => (
                        <span key={b} className="branch-tag">{b}</span>
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
                    <div className="empty-hint">输入说明并点击"保存存档"创建第一个存档</div>
                </div>
            )}

            {/* React Flow DAG */}
            {!loading && commits.length > 0 && (
                <div className="graph-container">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onNodeClick={onNodeClick}
                        nodeTypes={nodeTypes}
                        fitView
                        fitViewOptions={{ padding: 0.3 }}
                        minZoom={0.1}
                        maxZoom={2}
                        defaultEdgeOptions={{
                            type: "smoothstep",
                            style: { stroke: "var(--accent)", strokeWidth: 2 },
                        }}
                        proOptions={{ hideAttribution: true }}
                    >
                        <Background
                            variant={BackgroundVariant.Dots}
                            gap={20}
                            size={1}
                            color="var(--border-subtle)"
                        />
                        <Controls
                            showInteractive={false}
                            position="bottom-right"
                        />
                        <MiniMap
                            nodeStrokeColor="var(--accent)"
                            nodeColor="var(--bg-tertiary)"
                            maskColor="rgba(0, 0, 0, 0.6)"
                            style={{ background: "var(--bg-secondary)" }}
                        />
                    </ReactFlow>
                </div>
            )}
        </div>
    );
}
