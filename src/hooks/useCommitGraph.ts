// Hook to convert CommitInfo[] → React Flow nodes + edges using dagre layout
// See: /arch/adr-001-tauri-v2-migration.md

import { useMemo } from "react";
import type { Node, Edge } from "@xyflow/react";
import type { CommitInfo } from "../types";
import type { CommitNodeData } from "../components/CommitNode";
import dagre from "@dagrejs/dagre";

const NODE_WIDTH = 260;
const NODE_HEIGHT = 90;

/**
 * Auto-layout commit DAG using dagre:
 * 1. Build a dagre graph from commits + parent edges
 * 2. Run dagre layout to compute x/y positions
 * 3. Map back to React Flow nodes/edges
 */
export function useCommitGraph(
    commits: CommitInfo[],
    selectedCommit: string | null
): { nodes: Node[]; edges: Edge[] } {
    return useMemo(() => {
        if (commits.length === 0) return { nodes: [], edges: [] };

        // SHA → index map for edge validation
        const shaSet = new Set(commits.map((c) => c.hex_sha));

        // Create dagre graph
        const g = new dagre.graphlib.Graph();
        g.setGraph({
            rankdir: "TB",
            nodesep: 60,
            ranksep: 100,
            marginx: 20,
            marginy: 20,
        });
        g.setDefaultEdgeLabel(() => ({}));

        // Add nodes
        for (const commit of commits) {
            g.setNode(commit.hex_sha, { width: NODE_WIDTH, height: NODE_HEIGHT });
        }

        // Add edges (child → parent)
        for (const commit of commits) {
            for (const parentSha of commit.parents) {
                if (shaSet.has(parentSha)) {
                    g.setEdge(commit.hex_sha, parentSha);
                }
            }
        }

        // Run layout
        dagre.layout(g);

        // Build React Flow nodes from dagre positions
        const nodes: Node[] = commits.map((commit) => {
            const nodeWithPos = g.node(commit.hex_sha);
            return {
                id: commit.hex_sha,
                type: "commitNode",
                position: {
                    x: (nodeWithPos.x ?? 0) - NODE_WIDTH / 2,
                    y: (nodeWithPos.y ?? 0) - NODE_HEIGHT / 2,
                },
                data: {
                    hexSha: commit.hex_sha,
                    message: commit.message,
                    author: commit.author,
                    timestamp: commit.timestamp,
                    branches: commit.branches,
                    isSelected: selectedCommit === commit.hex_sha,
                    isCurrent: commit.is_current,
                } satisfies CommitNodeData,
                style: { width: NODE_WIDTH, height: NODE_HEIGHT },
            };
        });

        // Build edges
        const edges: Edge[] = [];
        for (const commit of commits) {
            for (const parentSha of commit.parents) {
                if (shaSet.has(parentSha)) {
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
