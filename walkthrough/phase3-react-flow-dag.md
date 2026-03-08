# Phase 3 Walkthrough: React Flow DAG 可视化

> 关联 ADR: [adr-001-tauri-v2-migration.md](file:///media/hr/Data/Codes/git-game-save-manager/arch/adr-001-tauri-v2-migration.md)
> 日期: 2026-03-08

## 变更摘要

将 CommitGraphPage 的 commit 列表替换为 React Flow DAG 图。

## 新增文件

### CommitNode.tsx

自定义 React Flow 节点组件：
- `Handle` top/bottom 连接点
- 显示 SHA（monospace）、message、author、timestamp、branch 标签
- 选中高亮（accent border + glow）

### useCommitGraph.ts

Commits → React Flow 数据转换 hook：
- **Lane 分配算法**：拓扑序遍历，first parent 继承 lane，merge parents 分配新 lane
- **坐标计算**：`x = lane * 300`, `y = index * 140`
- **边类型**：`smoothstep`（贝塞尔曲线）
- Memoized with `useMemo()`

## 变更文件

### CommitGraphPage.tsx

```diff
-import { ... } from "react";
+import { ReactFlow, MiniMap, Controls, Background, ... } from "@xyflow/react";
+import { useCommitGraph } from "../hooks/useCommitGraph";
+import { CommitNode } from "../components/CommitNode";

-<div className="commit-list">
-    {commits.map(...)}
-</div>
+<ReactFlow
+    nodes={nodes}
+    edges={edges}
+    nodeTypes={{ commitNode: CommitNode }}
+    fitView
+>
+    <Background variant="dots" />
+    <Controls />
+    <MiniMap />
+</ReactFlow>
```

### App.css

新增以下样式块：
- `.graph-page` — 全高 flex 布局
- `.graph-toolbar` — 固定顶部工具栏
- `.commit-node` 系列 — 节点 dark theme 样式
- `.commit-handle` — 连接点样式
- `.react-flow__*` — React Flow 组件 dark theme 覆盖

## 验证结果

- `npm run build`: ✅ 203 modules, 387KB JS
- `tsc`: ✅ 无类型错误
