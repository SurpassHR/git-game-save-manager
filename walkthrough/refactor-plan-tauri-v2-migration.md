# 重构计划: Tauri v2 迁移

> 关联 ADR: [adr-001-tauri-v2-migration.md](file:///media/hr/Data/Codes/git-game-save-manager/arch/adr-001-tauri-v2-migration.md)

## 概述

将 git-game-save-manager 从 Python + PyQt5 全面迁移到 Tauri v2 + React + TypeScript。本次迁移分为多个阶段，每个阶段独立可验证。

## Phase 1：项目脚手架搭建（本次执行范围）

### 目标

建立 Tauri v2 + React + TypeScript 项目基础结构，能够 `npm run tauri dev` 成功启动空壳应用。

### 步骤

1. **清理 v1 代码** — 移除 `core/`, `ui/`, `config/`, `lab/`, `main.py`, `init_dev_env.sh`（v1 保留在 `main` 分支）
2. **初始化 Tauri v2 项目** — 使用 `create-tauri-app` 的 react-ts 模板
3. **配置 Tauri v2** — 更新 `tauri.conf.json`（窗口标题、尺寸、identifier）
4. **建立后端目录结构** — 创建 `src-tauri/src/commands/`, `services/`, `models/` 模块
5. **建立前端目录结构** — 创建 `src/pages/`, `store/`, `services/`, `types/`, `hooks/`
6. **安装核心依赖** — `@xyflow/react`(React Flow), `zustand`, `@tauri-apps/api`
7. **更新 `.gitignore`** — 添加 `node_modules/`, `target/`, `dist/` 等
8. **验证** — `npm run tauri dev` 成功启动窗口

### 验证方式

```bash
# dev 模式启动 Tauri 窗口
npm run tauri dev
# 预期：打开一个带 React 页面的桌面窗口，无报错
```

---

## Phase 2：Rust 后端 Git 服务（后续迭代）

- 实现 `git_service.rs`（使用 git2 crate）
- 暴露 Tauri Commands: `list_commits`, `create_commit`, `checkout_commit`, `get_branches`
- 前端 IPC 封装层

## Phase 3：前端 DAG 可视化（后续迭代）

- React Flow 集成
- Commit 节点自定义组件
- 贝塞尔曲线边
- Minimap

## Phase 4：完整功能对齐 + 新特性（后续迭代）

- 配置管理页面
- 主题切换
- 多游戏管理
- 自动监控
