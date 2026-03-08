# Feature Plan: Commit Context Menu (恢复/删除/修改说明)

## 目标 (Goal Description)
在 React Flow 画布中的 Commit 节点上实现右键菜单，提供三种高级 Git 操作：
1. **恢复到此存档 (Revert)**: 放弃当前所有未提交的修改，并将 HEAD 和工作区强制重置 (`git reset --hard`) 到目标 commit。
2. **删除此存档 (Delete)**: 这是一个危险操作。对于游离的叶子节点，采用 branch 强删或者通过 `reset` 实现；如果是在历史中间，则涉及到复杂的 `rebase`。考虑到本游戏存档管理器的场景（通常是单线或者简单的多分支 fork），我们将通过 `git push / branch -D` 或者直接修改 refs 进行安全剥离。*为简单且安全起见，初始版本仅支持软删除（移动 HEAD 并丢弃孤立节点），更复杂的历史改写后续再迭代。* 
> **注意/⚠️ 修正方案**: 在存档管理器中，用户所说的“删除存档”本质上是丢弃某个 commit 之后的历史。我们会实现一个 `hard_reset` 来“回到过去并抹除未来”。如果是要删除历史树中间的单个 commit，则暂不在 V1 实现（需要 interactive rebase 机制）。
3. **修改存档说明 (Amend Message)**: 只能修改当前 HEAD 的说明 (`git commit --amend`)。如果是历史节点的说明，同样需要 `rebase`，因此目前将限制只能修改 `isCurrent = true` 节点的说明。

## 架构变更 (Proposed Changes)

### Backend (Rust / Tauri)
#### [MODIFY] [src-tauri/src/services/git_service.rs](file:///media/hr/Data/Codes/git-game-save-manager/src-tauri/src/services/git_service.rs)
- `reset_hard(repo_path, commit_sha)`: 将 HEAD 强行指向指定 commit，并清理工作区。
- `amend_commit(repo_path, new_message)`: 修改当前 HEAD 指向的 commit 的 message。

#### [MODIFY] [src-tauri/src/commands/git_commands.rs](file:///media/hr/Data/Codes/git-game-save-manager/src-tauri/src/commands/git_commands.rs)
- 暴露 `reset_hard` 和 `amend_commit`  Tauri Cmd。
- 注册进 `main.rs`。

### Frontend (React / TypeScript)
#### [MODIFY] [src/services/gitService.ts](file:///media/hr/Data/Codes/git-game-save-manager/src/services/gitService.ts)
- 添加 `resetHard` 和 `amendCommit` 的封装。

#### [NEW] `src/components/ContextMenu.tsx`
- 实现一个悬浮的右键菜单组件 UI（包含三个按钮项）。

#### [MODIFY] [src/pages/CommitGraphPage.tsx](file:///media/hr/Data/Codes/git-game-save-manager/src/pages/CommitGraphPage.tsx)
- 监听 React Flow 的 `onNodeContextMenu` 事件，捕获鼠标坐标和目标 Node。
- 在页面顶层渲染 `ContextMenu`。
- 实现菜单动作的回调逻辑，并配合 `Tauri Dialog` 呼出确认框（防止误操作）以及输入框（用于 Amend）。

## Verification Plan

### Manual Testing
1. **唤出菜单**:
    - 右键点击任意节点，弹出菜单。
    - 点击画布空白处，菜单消失。
2. **恢复/删除操作 (Reset Hard)**:
    - 选择 "硬重置到此存档 (危险)"。
    - 弹出 Tauri 原生 Confirm 窗口警告。
    - 确认后，图谱刷新，对应节点之前的后续节点由于变为孤儿节点并可能会在拓扑图中被丢弃。
3. **修改说明 (Amend)**:
    - 仅能在有 `isCurrent: true` 标识的节点上点击 "修改说明"。
    - 弹出 Tauri Prompt 窗口，输入新 message。
    - 确认后，图谱刷新，可见节点文本已改变且 Hash 变化。
