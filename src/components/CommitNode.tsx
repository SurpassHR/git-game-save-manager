// Custom React Flow node for commit visualization
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";

export interface CommitNodeData {
    hexSha: string;
    message: string;
    author: string;
    timestamp: number;
    branches: string[];
    isSelected: boolean;
    isCurrent: boolean;
    [key: string]: unknown;
}

function formatTime(ts: number) {
    return new Date(ts * 1000).toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function CommitNodeComponent({ data }: NodeProps) {
    const d = data as CommitNodeData;
    return (
        <div className={`commit-node ${d.isSelected ? "commit-node--selected" : ""} ${d.isCurrent ? "commit-node--current" : ""}`}>
            <Handle type="target" position={Position.Top} className="commit-handle" />

            <div className="commit-node__header">
                <span className="commit-node__sha">{d.hexSha}</span>
                <div style={{ display: "flex", gap: "4px" }}>
                    {d.isCurrent && (
                        <span className="commit-node__current-badge">📍 当前存档</span>
                    )}
                    {(d.branches as string[])?.length > 0 && (
                        <div className="commit-node__branches">
                            {(d.branches as string[]).map((b: string) => (
                                <span key={b} className="commit-node__branch">{b}</span>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div className="commit-node__message">{d.message || "(no message)"}</div>

            <div className="commit-node__footer">
                <span className="commit-node__author">{d.author}</span>
                <span className="commit-node__time">{formatTime(d.timestamp)}</span>
            </div>

            <Handle type="source" position={Position.Bottom} className="commit-handle" />
        </div>
    );
}

export const CommitNode = memo(CommitNodeComponent);
