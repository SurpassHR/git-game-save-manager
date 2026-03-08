// Context Menu Component for React Flow nodes
// See: /walkthrough/implementation-plan-context-menu.md

import { useEffect, useRef } from "react";

export interface ContextMenuProps {
    x: number;
    y: number;
    commitSha: string;
    onClose: () => void;
    onCheckout: (sha: string) => void;
    onDeleteCommit: (sha: string) => void;
    onAmendMessage: (sha: string) => void;
    onCreateBranch: (sha: string) => void;
}

export function ContextMenu({
    x,
    y,
    commitSha,
    onClose,
    onCheckout,
    onDeleteCommit,
    onAmendMessage,
    onCreateBranch,
}: ContextMenuProps) {
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                onClose();
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [onClose]);

    useEffect(() => {
        function handleKeyDown(event: KeyboardEvent) {
            if (event.key === "Escape") {
                onClose();
            }
        }
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [onClose]);

    return (
        <div ref={menuRef} className="context-menu" style={{ top: y, left: x }}>
            <div className="context-menu__header">
                存档: <span className="context-menu__sha">{commitSha}</span>
            </div>

            <button
                className="context-menu__item"
                onClick={() => { onCreateBranch(commitSha); onClose(); }}
            >
                <span className="context-menu__icon">🌿</span>
                <span>从此处创建分支</span>
            </button>

            <button
                className="context-menu__item"
                onClick={() => { onAmendMessage(commitSha); onClose(); }}
            >
                <span className="context-menu__icon">✏️</span>
                <span>修改说明</span>
            </button>

            <button
                className="context-menu__item"
                onClick={() => { onDeleteCommit(commitSha); onClose(); }}
            >
                <span className="context-menu__icon">🗑️</span>
                <span>删除此存档</span>
            </button>

            <div className="context-menu__separator" />

            <button
                className="context-menu__item"
                onClick={() => { onCheckout(commitSha); onClose(); }}
            >
                <span className="context-menu__icon">📂</span>
                <span>切换到此存档</span>
            </button>
        </div>
    );
}
