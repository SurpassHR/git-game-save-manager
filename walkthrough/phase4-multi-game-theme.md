# Phase 4 Walkthrough: 多游戏管理 + 主题 + UI 增强

> 日期: 2026-03-08

## 变更摘要

将单仓库配置升级为多游戏 Profile 管理，实现实际生效的 light/dark 主题切换。

## 数据模型变更

```diff
 pub struct AppConfig {
     pub theme: String,
-    pub repo_path: String,
+    pub active_profile_id: String,
+    pub profiles: Vec<GameProfile>,
 }

+pub struct GameProfile {
+    pub id: String,
+    pub name: String,
+    pub repo_path: String,
+    pub icon: String,
+}
```

## 新增 Tauri Commands

- `add_profile(name, repo_path, icon)` — 创建 profile + 自动激活首个
- `remove_profile(id)` — 删除 + 自动切换 active
- `set_active_profile(id)` — 切换当前游戏

## 主题系统

```diff
-:root {
+:root, [data-theme="dark"] {
   --bg-primary: #1a1b1e;
   ...
 }
+
+[data-theme="light"] {
+  --bg-primary: #f8f9fa;
+  ...
+}
```

App.tsx 在 config 变化时应用 `document.documentElement.dataset.theme`

## 验证结果

- `cargo check`: ✅
- `npm run build`: ✅ 204 modules, 392KB
