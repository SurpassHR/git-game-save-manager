# Git Game Save Manager v2 — 设计语言与规范 (Design Language & Patterns)

本文档是由 AI 提取并整理的当前项目 UX/UI 规范、状态管理与异常处理模式。在后续开发中，各类新增组件与逻辑必须遵循以下规范，确保“按图索骥”且保持代码风格的高度一致性。

## 1. 颜色模式与主题变量 (Color & Theme System)
项目依赖原生的 CSS Variables 实现动态主题切换，通过设置 `document.documentElement.dataset.theme = "light" | "dark"` 控制。

* **背景分层**: `var(--bg-primary)` (应用底色) / `var(--bg-secondary)` (卡片/侧边栏) / `var(--bg-tertiary)` (输入框/悬浮/次要元素)
* **文本分层**: `var(--text-primary)` (主文本) / `var(--text-secondary)` (次要文本) / `var(--text-muted)` (辅助/说明文本) / `var(--text-accent)` (强调文本)
* **状态与交互**: `var(--accent)` (主色, 默认 Blue) / `var(--success)` (成功, Green) / `var(--danger)` (危险状态, Red) / `var(--warning)` (警告, Yellow)

## 2. UI 组件规范与 CSS 策略 (UI Components & Layout)
整体未引入第三方组件库或 TailwindCSS，采用基于 class 名称的模块化+原子化 CSS 策略。

### 2.1 基础布局 (Layout Patterns)
* **App 布局**: 使用 `.app-layout` (100vh flex 布局) 分割 `.sidebar` 和 `.main-content`。
* **页面容器**: 主内容区包含 `.page` 类名 (带内边距与 `max-width: 900px` 限制)。
* **卡片布局**: 内容使用 `.card` 进行区块封装，头部使用 `.card-header` (包含 `.card-title` 和 `.card-description`)。

### 2.2 交互组件 (Form & Controls)
* **按钮 (Buttons)**: 
  * 基础类 `.btn`。
  * 变体类：`.btn-primary` (强操作), `.btn-success` (确认操作), `.btn-danger` (毁坏性操作), `.btn-sm` (小尺寸), `.icon-btn` (纯图标按钮)。
* **输入框 (Inputs)**: 使用 `.input` 以及 `.profile-select` 进行基础表单样式封装。

### 2.3 状态视图 (Status Views)
* **空状态 (Empty State)**: 使用 `.empty-state` 包裹 `.empty-icon`, `.empty-text` 和 `.empty-hint`。
* **加载与异常**: 
  * 阻断错误展示使用 `.error-banner` (带背景虚化与警示图标)。
  * 等待加载展示使用 `.loading-spinner`。

### 2.4 特定业务组件 (Domain Components)
* **Commit 节点 (React Flow)**: `.commit-node` 用于 DAG 可视化。选中状态应用 `.commit-node--selected`，提供 `.commit-node__header`, `.commit-node__sha` 等内部子元素约定。

## 3. 异常处理模式 (Error Handling Pattern)
项目采用集中式的异常捕获与 UI 驱动渲染。

1. **逻辑层捕获 (Store Actions)**: 
   在 Zustand store 的异步 action 中，使用 `try...catch` 截获全部 Tauri IPC 返回的错误，并记录为字符串：
   ```typescript
   try {
       // ...业务调用
   } catch (e) {
       set({ error: String(e) });
   }
   ```
2. **重置触发**: 执行新的关键操作（例如 `initRepo`、`switchProfile`）时会先清理上次错误：`setError(null)`。
3. **UI 渲染**: 页面组件 (如 `ConfigPage`) 直接从 store 绑定 `error`，如有报错则在页面顶部展示：
   ```tsx
   {error && <div className="error-banner">⚠️ {error}</div>}
   ```

## 4. 数据转换逻辑 (DTO / VO)
业务核心数据由 Rust `serde` 序列化为 JSON，并在前端的 `src/types/index.ts` 进行 Type 约束对应，保证 IPC 调用的类型安全。

* **配置实体**: `AppConfig`, `GameProfile`
* **Git 实体**: `CommitInfo`, `BranchInfo`
> **AI 指令**: 每次 Tauri Rust 后端的 Model 发生 Schema 修改时，必须同步修改 `src/types/index.ts`。

## 5. 通用工具类 (Utils)
* **日期格式化**: 目前零散分布于组件内 (如 `CommitNode.tsx` 内的 `formatTime`)，使用 `toLocaleString("zh-CN")`，后续若有复用需求，可提取至 `src/utils/dateFormatter.ts` 中。
