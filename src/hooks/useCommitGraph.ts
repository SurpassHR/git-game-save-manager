// Hook to convert CommitInfo[] → React Flow nodes + edges
// See: /arch/adr-001-tauri-v2-migration.md

import { useMemo } from "react";
import type { Node, Edge } from "@xyflow/react";
import type { CommitInfo } from "../types";
import type { CommitNodeData } from "../components/CommitNode";

const NODE_WIDTH = 260;
const NODE_HEIGHT = 90;
const GAP_X = 300;
const GAP_Y = 140;

/**
 * Auto-layout algorithm for commit DAG:
 * 1. Commits arrive in topological+time order (newest first) from Rust
 * 2. Assign columns: track active "lanes" — each fork gets a new lane
 * 3. Assign rows: sequential index
 */
export function useCommitGraph(
    commits: CommitInfo[],
    selectedCommit: string | null
): { nodes: Node[]; edges: Edge[] } {
    return useMemo(() => {
        if (commits.length === 0) return { nodes: [], edges: [] };

        // SHA → index map for quick lookup
        const shaIndex = new Map<string, number>();
        commits.forEach((c, i) => shaIndex.set(c.hex_sha, i));

        // Lane assignment: track which SHA occupies which column
        const laneMap = new Map<string, number>();
        const activeLanes: (string | null)[] = [];

        function getFreeLane(): number {
            const idx = activeLanes.indexOf(null);
            if (idx !== -1) return idx;
            activeLanes.push(null);
            return activeLanes.length - 1;
        }

        // First pass: assign lanes
        for (let i = 0; i < commits.length; i++) {
            const commit = commits[i];

            // Check if this commit already has a lane (assigned by a child)
            if (!laneMap.has(commit.hex_sha)) {
                const lane = getFreeLane();
                laneMap.set(commit.hex_sha, lane);
                activeLanes[lane] = commit.hex_sha;
            }

            const myLane = laneMap.get(commit.hex_sha)!;

            // Assign lanes to parents
            commit.parents.forEach((parentSha, pIdx) => {
                if (!laneMap.has(parentSha)) {
                    if (pIdx === 0) {
                        // First parent inherits the same lane
                        laneMap.set(parentSha, myLane);
                        activeLanes[myLane] = parentSha;
                    } else {
                        // Additional parents get new lanes (merge branches)
                        const newLane = getFreeLane();
                        laneMap.set(parentSha, newLane);
                        activeLanes[newLane] = parentSha;
                    }
                }
            });

            // If this commit has no children claiming its lane later, free it
            // (handled implicitly since parents inherit)
        }

        // Build nodes
        const nodes: Node[] = commits.map((commit, i) => {
            const lane = laneMap.get(commit.hex_sha) ?? 0;
            return {
                id: commit.hex_sha,
                type: "commitNode",
                position: {
                    x: lane * GAP_X,
                    y: i * GAP_Y,
                },
                data: {
                    hexSha: commit.hex_sha,
                    message: commit.message,
                    author: commit.author,
                    timestamp: commit.timestamp,
                    branches: commit.branches,
                    isSelected: selectedCommit === commit.hex_sha,
                } satisfies CommitNodeData,
                style: { width: NODE_WIDTH, height: NODE_HEIGHT },
            };
        });

        // Build edges (child → parent, so source=child, target=parent)
        const edges: Edge[] = [];
        for (const commit of commits) {
            for (const parentSha of commit.parents) {
                if (shaIndex.has(parentSha)) {
                    edges.push({
                        id: `${commit.hex_sha}-${parentSha}`,
                        source: commit.hex_sha,
                        target: parentSha,
                        type: "smoothstep",
                        animated: false,
                        style: {
                            stroke: "var(--accent)",
                            strokeWidth: 2,
                        },
                    });
                }
            }
        }

        return { nodes, edges };
    }, [commits, selectedCommit]);
}
