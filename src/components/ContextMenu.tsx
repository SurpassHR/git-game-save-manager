// Context Menu Component for React Flow nodes
// See: /walkthrough/implementation-plan-context-menu.md

import { useEffect, useRef } from "react";

export interface ContextMenuProps {
    x: number;
    y: number;
    commitSha: string;
    isCurrent: boolean;
    onClose: () => void;
    onResetHard: (sha: string) => void;
    onAmendMessage: (sha: string) => void;
}

export function ContextMenu({
    x,
    y,
    commitSha,
    isCurrent,
    onClose,
    onResetHard,
    onAmendMessage,
}: ContextMenuProps) {
    const menuRef = useRef<HTMLDivElement>(null);

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                onClose();
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [onClose]);

    // Close on Escape
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
        <div
            ref={menuRef}
            className="context-menu"
            style={{
                top: y,
                left: x,
            }}
        >
            <div className="context-menu__header">
                存档: <span className="context-menu__sha">{commitSha}</span>
            </div>

            <button
                className="context-menu__item"
                onClick={() => {
                    onResetHard(commitSha);
                    onClose();
                }}
            >
                <span className="context-menu__icon">⚠️</span>
                <span>恢复并删除后续存档</span>
            </button>

            <button
                className="context-menu__item"
                disabled={!isCurrent}
                onClick={() => {
                    if (isCurrent) {
                        onAmendMessage(commitSha);
                        onClose();
                    }
                }}
                title={!isCurrent ? "只能修改当前所处存档的说明" : ""}
            >
                <span className="context-menu__icon">✏️</span>
                <span>修改当前说明</span>
            </button>
        </div>
    );
}
