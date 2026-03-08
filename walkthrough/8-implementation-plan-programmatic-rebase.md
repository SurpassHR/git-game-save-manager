# Feature Plan: 历史存档改名 (Programmatic Rebase)

## 目标 (Goal Description)
允许用户对 Git 树上的**任意历史 commit** 修改说明（message）。因为 Git 的不可变性，这本质上需要执行一次自动化的 `rebase` 过程。

## 场景分析
在游戏存档管理中，我们可能存在：
1. **纯单线结构**：A -> B -> C (HEAD)。修改 B 后，只要把 C 重新挂在新的 B' 后即可。
2. **多分支结构 (平行宇宙)**：存档产生分支。目前我们的 UI 虽然渲染了分支节点，但在底层依然是标准 Git 树结构。
*由于 `libgit2` 实现完整的包含所有分支的拓扑重写非常复杂（极易引发 Detached HEAD 和引用丢失），第一阶段我们采取**单线安全重写策略***：只针对当前 `HEAD` 所在的分支链路进行从指定修改点到 `HEAD` 的顺藤摸瓜式重写。若节点存在其他分支引用，可能会导致其他分支依旧指向老节点（引发树的分裂），这属于高级特性，本阶段重点保证当前活跃存档线的无缝改名。

## 设计方案 (Proposed Changes)

### Backend (Rust)
#### [MODIFY] [src-tauri/src/services/git_service.rs](file:///media/hr/Data/Codes/git-game-save-manager/src-tauri/src/services/git_service.rs)
替换现有的 `amend_commit` 简单逻辑，改为强大的历史重写函数：
1. **寻找目标**：在当前 `HEAD` 的历史回溯中找到目标 commit。
2. **记录重放路径**：收集从修该点到 `HEAD` 之间的所有 commit 的 SHA。
3. **Checkout 并 Amend**：checkout 到目标点，执行 `amend` 生成新的 commit (`new_base`)。
4. **循环重放 (Cherry-pick / Commit)**：沿着第 2 步收集的路径，依次把每一个旧 commit 的改动 `cherry-pick` 到 `new_base` 之后形成新的提交。
5. **更新指针**：完成后，将原来的分支（或 HEAD）强行指向最新重放完成的节点。

### Frontend (React/TS)
#### [MODIFY] [src/components/ContextMenu.tsx](file:///media/hr/Data/Codes/git-game-save-manager/src/components/ContextMenu.tsx)
- 移除 `disabled={!isCurrent}` 的限制条件。
- 允许所有节点呼出修改说明的 Prompt。

#### [MODIFY] [src/pages/CommitGraphPage.tsx](file:///media/hr/Data/Codes/git-game-save-manager/src/pages/CommitGraphPage.tsx)
- 由于重写历史会改变大量节点的 SHA，在调用 `amendCommit` 后必须执行 `loadCommits()` 保证全量图谱刷新。这在之前的代码中已经涵盖。

## 风险与应对 (Verification Plan)
- **风险**: 修改远古节点会导致大量的 Git 哈希重算，如果历史过长，可能会有极短暂的卡顿。另外如果在重写期间遭遇冲突（按理说仅重放 commit tree 不会有冲突），必须进行安全回滚 (`git reset --hard ORIG_HEAD`)。
- **验证**:
  1. 创建节点 A、B、C。
  2. 右键 B 修改为 "B-rename"。
  3. 预期图谱刷新后，展示 A -> B-rename -> C'，且 `HEAD` 重回 C'。  
