# Walkthrough: Phase 1 — Tauri v2 项目脚手架搭建

> 关联 ADR: [adr-001-tauri-v2-migration.md](file:///media/hr/Data/Codes/git-game-save-manager/arch/adr-001-tauri-v2-migration.md)
> 日期: 2026-03-08

## 变更摘要

将 git-game-save-manager 从 Python + PyQt5 迁移到 Tauri v2 + React + TypeScript 项目骨架。

## 执行步骤

### 1. 移除 v1 代码

删除 `core/`, `ui/`, `config/`, `lab/`, `main.py`, `init_dev_env.sh`。v1 代码在 `main` 分支保留。

### 2. 初始化 Tauri v2

```bash
npx -y create-tauri-app@latest ./ --template react-ts --manager npm --force --yes
npm install
```

> ⚠️ `create-tauri-app --force` 会清空目标目录，导致 `/arch`, `/design`, `/walkthrough`, `.agents` 被删除，需手动恢复

### 3. 修复 Node 18 兼容性

Vite 7.3 的 dev server 在 Node 18 上崩溃（`crypto.hash is not a function`），降级到 Vite 6：

```bash
npm install vite@^6 @vitejs/plugin-react@^4
```

### 4. 配置项目

| 文件 | 变更 |
|---|---|
| `tauri.conf.json` | productName, identifier, 窗口 1280x720 居中 |
| `Cargo.toml` | 包名 `git-game-save-manager`, 添加 `git2`, `toml`, `chrono` |
| `main.rs` | 更新 lib crate 引用名 |
| `lib.rs` | 注册 `commands`, `services`, `models` 子模块 |

### 5. 创建后端模块结构

```
src-tauri/src/
├── commands/
│   ├── mod.rs
│   ├── git_commands.rs    ← list_commits, get_branches
│   └── config_commands.rs ← get_config, set_config
├── services/
│   ├── mod.rs
│   ├── git_service.rs     ← git2 封装
│   └── config_service.rs  ← TOML 读写
├── models/
│   ├── mod.rs
│   ├── commit.rs          ← CommitInfo, BranchInfo
│   └── config.rs          ← AppConfig
├── lib.rs
└── main.rs
```

### 6. 创建前端模块结构

```
src/
├── components/     ← 通用 UI 组件
├── hooks/          ← React Hooks
├── pages/          ← 页面组件
├── services/
│   └── gitService.ts  ← Tauri IPC 封装
├── store/
│   └── index.ts       ← Zustand store
├── types/
│   └── index.ts       ← TS 类型定义
├── App.tsx
├── App.css
└── main.tsx
```

### 7. 安装依赖

```bash
npm install @xyflow/react zustand
```

## 验证结果

| 检查项 | 结果 |
|---|---|
| `cargo check` | ✅ 532 crates 编译通过 |
| `npm run build` | ✅ 32 modules, 194KB JS bundle |
| `npm run tauri dev` | ✅ 桌面窗口成功启动 |
| 文档目录保留 | ✅ `/arch`, `/design`, `/walkthrough`, `.agents` 完好 |

## 启动截图

![Tauri v2 App Launch](/home/hr/.gemini/antigravity/brain/fafe3c25-3039-446d-a082-0923de4831f0/tauri_v2_launch.png)

## 后续步骤

- **Phase 2**: 实现 Rust Git 服务 + 前端 IPC 调用
- **Phase 3**: React Flow DAG 可视化
- **Phase 4**: 完整功能对齐 + 新特性
