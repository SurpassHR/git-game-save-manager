// Commit detail side panel
// See: /walkthrough/refactor-plan-tauri-v2-migration.md

import type { CommitInfo } from "../types";

interface CommitDetailPanelProps {
    commit: CommitInfo;
    onCheckout: (sha: string) => void;
    onClose: () => void;
}

function formatFullTime(ts: number) {
    return new Date(ts * 1000).toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}

export function CommitDetailPanel({
    commit,
    onCheckout,
    onClose,
}: CommitDetailPanelProps) {
    return (
        <div className="detail-panel">
            <div className="detail-panel__header">
                <h3 className="detail-panel__title">存档详情</h3>
                <button className="btn btn-sm" onClick={onClose}>
                    ✕
                </button>
            </div>

            <div className="detail-panel__body">
                <div className="detail-field">
                    <span className="detail-label">SHA</span>
                    <span className="detail-value detail-value--mono">
                        {commit.hex_sha}
                    </span>
                </div>

                <div className="detail-field">
                    <span className="detail-label">说明</span>
                    <span className="detail-value">{commit.message || "(无描述)"}</span>
                </div>

                <div className="detail-field">
                    <span className="detail-label">作者</span>
                    <span className="detail-value">{commit.author}</span>
                </div>

                <div className="detail-field">
                    <span className="detail-label">时间</span>
                    <span className="detail-value">
                        {formatFullTime(commit.timestamp)}
                    </span>
                </div>

                {commit.parents.length > 0 && (
                    <div className="detail-field">
                        <span className="detail-label">父节点</span>
                        <span className="detail-value detail-value--mono">
                            {commit.parents.join(" → ")}
                        </span>
                    </div>
                )}

                {commit.branches.length > 0 && (
                    <div className="detail-field">
                        <span className="detail-label">分支</span>
                        <div className="detail-branches">
                            {commit.branches.map((b) => (
                                <span key={b} className="branch-tag">
                                    {b}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="detail-panel__actions">
                <button
                    className="btn btn-primary"
                    onClick={() => onCheckout(commit.hex_sha)}
                    style={{ width: "100%" }}
                >
                    ⏪ 恢复到此存档
                </button>
            </div>
        </div>
    );
}
