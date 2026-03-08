# Feature Plan: 当前存档指示器 (Current Save Indicator)

## 目标 (Goal Description)
在关系图画布中直观地标记出当前所处的存档位置 (git HEAD)，让用户明确知道自己目前应用的是哪一个存档状态。

## 设计方案 (Proposed Changes)

为了实现该目标，我们需要通过 Tauri IPC 将当前的 HEAD 状态传递给前端，并在 React Flow node 中渲染专属样式。由于这涉及全局接口 Schema 修改，这是明确的前后端联动：

### Backend (Rust)
#### [MODIFY] [src-tauri/src/models/commit.rs](file:///media/hr/Data/Codes/git-game-save-manager/src-tauri/src/models/commit.rs)
- 在 `CommitInfo` struct 中新增 `pub is_current: bool` 字段。

#### [MODIFY] [src-tauri/src/services/git_service.rs](file:///media/hr/Data/Codes/git-game-save-manager/src-tauri/src/services/git_service.rs)
- 在 `list_commits` 函数中获取当前 `HEAD` 对应的 commit hash。
- 遍历 commits 时，比对 SHA 将对应的 commit `is_current` 设为 `true`。

### Frontend (React/TS)
#### [MODIFY] [src/types/index.ts](file:///media/hr/Data/Codes/git-game-save-manager/src/types/index.ts)
- 更新 `CommitInfo` 接口，同步新增 `is_current: boolean`。

#### [MODIFY] [src/hooks/useCommitGraph.ts](file:///media/hr/Data/Codes/git-game-save-manager/src/hooks/useCommitGraph.ts)
- 在映射 `CommitNodeData` 时注入 `isCurrent: commit.is_current`。

#### [MODIFY] [src/components/CommitNode.tsx](file:///media/hr/Data/Codes/git-game-save-manager/src/components/CommitNode.tsx)
- 接收 `isCurrent` 参数。当为 `true` 时，在节点 Header 增加「📍 当前存档」标识（Badge）。
- 添加 `commit-node--current` 类名。

#### [MODIFY] [src/App.css](file:///media/hr/Data/Codes/git-game-save-manager/src/App.css)
- 增加 `.commit-node--current` 相关的边框高亮样式（例如使用 `--success` 颜色高亮）。
- 增加 `.commit-node__current-badge` 的 CSS 代码。

## 验证计划 (Verification Plan)
### 手动验证 (Manual Testing)
1. 编译并启动桌面端应用。
2. 观察当前加载的游戏存档历史树，确认最新的或 checkout 过后的存档节点上出现「📍 当前存档」标识。
3. 尝试点击旧提交进行 Checkout (读档)，刷新后确认标识正确转移到了旧节点上。
