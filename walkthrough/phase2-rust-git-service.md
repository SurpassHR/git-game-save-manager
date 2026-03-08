# Phase 2 Walkthrough: Rust Git 服务 + 前端集成

> 关联 ADR: [adr-001-tauri-v2-migration.md](file:///media/hr/Data/Codes/git-game-save-manager/arch/adr-001-tauri-v2-migration.md)
> 日期: 2026-03-08

## 变更摘要

完成 Tauri v2 的 Rust 后端 Git 服务和前端 IPC 集成，搭建了完整的 UI 框架。

## Rust 后端

### lib.rs 变更

移除 `greet` 占位命令，注册 7 个真实 commands：

```diff
-#[tauri::command]
-fn greet(name: &str) -> String { ... }
-
-.invoke_handler(tauri::generate_handler![greet])
+use commands::git_commands::*;
+use commands::config_commands::*;
+
+.invoke_handler(tauri::generate_handler![
+    list_commits, get_branches, init_repo, create_commit, checkout_commit,
+    get_config, set_config,
+])
```

### git_service.rs 新增功能

- `init_repo()` — 使用 `Repository::init()`
- `create_commit()` — `IndexAddOption::DEFAULT` 暂存所有文件 + 处理已删除文件 + commit
- `checkout_commit()` — `revparse_single()` 查找 commit + `checkout_tree()` + `set_head_detached()`
- `list_commits()` — 新增 branch 映射，支持 `TOPOLOGICAL | TIME` 排序

### config_service.rs 修复

```diff
-fn config_path() -> PathBuf {
-    PathBuf::from("config.toml")
-}
+fn config_path() -> PathBuf {
+    let base = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
+    let app_dir = base.join("git-game-save-manager");
+    let _ = fs::create_dir_all(&app_dir);
+    app_dir.join("config.toml")
+}
```

## 前端

### UI 架构

```
App.tsx (sidebar + main-content)
├── ConfigPage.tsx    — 存档目录选择 + 仓库初始化
└── CommitGraphPage.tsx — commit 列表 + 创建 + 恢复
```

### Zustand Store 扩展

新增异步 actions：`loadConfig()`, `saveConfig()`, `loadCommits()`，通过 IPC 与 Rust 后端通信。

## 验证结果

- `cargo check`: ✅ 541 crates
- `npm run build`: ✅ 40 modules, 202KB JS
- `npm run tauri dev`: ✅ 桌面窗口启动，新 UI 渲染正常
