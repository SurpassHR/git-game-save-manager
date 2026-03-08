# ADR-001: 从 PyQt5 迁移到 Tauri v2

## 状态

已批准（基于 [project_analysis.md.resolved](file:///media/hr/Data/Codes/git-game-save-manager/arch/project_analysis.md.resolved) 方案 B）

## 背景

当前 v1 使用 Python + PyQt5 + PyQt-Fluent-Widgets 构建，存在以下核心问题：
- PyQt5 已 EOL
- 多重继承导致职责混杂
- 打包体积大（PyInstaller ~100MB+）
- QGraphicsView 的 DAG 可视化能力弱于 Web 生态

## 决策

采用 **Tauri v2 + React + TypeScript** 重写整个项目。

## 技术选型

| 层次 | 选型 | 版本 | 理由 |
|---|---|---|---|
| 桌面框架 | Tauri v2 | latest stable | Rust 后端，体积小（~10MB），性能好 |
| 前端框架 | React | 18+ | 生态丰富，DAG 可视化库多 |
| 语言 | TypeScript | 5.x | 类型安全 |
| 构建工具 | Vite | 6.x | 快速 HMR |
| 状态管理 | Zustand | 5.x | 轻量、TypeScript 友好 |
| 图可视化 | React Flow | 12.x | 专业 DAG 可视化、开箱即用 minimap/controls |
| UI 组件库 | 待定（后续 ADR） | — | 先用原生 CSS + 自定义组件 |
| Git 操作 | Rust `git2` crate | — | 通过 Tauri Commands 暴露给前端 |
| 配置管理 | `serde` + TOML | — | Rust 侧持久化 |

## 系统分层

```
┌─────────────────────────────────────────┐
│            Frontend (React/TS)          │
│  ┌───────────┐ ┌──────────┐ ┌────────┐ │
│  │  Pages    │ │ Widgets  │ │ Store  │ │
│  └─────┬─────┘ └────┬─────┘ └───┬────┘ │
│        │            │           │       │
│  ┌─────▼────────────▼───────────▼────┐  │
│  │         Tauri IPC (invoke)        │  │
│  └───────────────┬───────────────────┘  │
├──────────────────┼──────────────────────┤
│            Backend (Rust)               │
│  ┌───────────────▼───────────────────┐  │
│  │         Tauri Commands            │  │
│  │  ┌──────────┐  ┌───────────────┐  │  │
│  │  │ git_cmds │  │ config_cmds   │  │  │
│  │  └────┬─────┘  └──────┬────────┘  │  │
│  │       │               │           │  │
│  │  ┌────▼─────┐  ┌──────▼────────┐  │  │
│  │  │ git2 lib │  │ serde + TOML  │  │  │
│  │  └──────────┘  └───────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 目录结构

```
git-game-save-manager/
├── arch/                     # 架构决策文档
├── design/                   # 设计规范文档
├── walkthrough/              # 重构记录文档
├── src/                      # 前端源码 (React/TS)
│   ├── assets/               # 静态资源
│   ├── components/           # 通用 UI 组件
│   ├── pages/                # 页面级组件
│   ├── store/                # Zustand 状态管理
│   ├── services/             # Tauri IPC 封装
│   ├── types/                # TypeScript 类型定义
│   ├── hooks/                # 自定义 React Hooks
│   ├── App.tsx               # 根组件
│   ├── App.css               # 全局样式
│   └── main.tsx              # 入口
├── src-tauri/                # Rust 后端源码
│   ├── src/
│   │   ├── commands/         # Tauri Command handlers
│   │   │   ├── mod.rs
│   │   │   ├── git_commands.rs
│   │   │   └── config_commands.rs
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── mod.rs
│   │   │   ├── git_service.rs
│   │   │   └── config_service.rs
│   │   ├── models/           # 数据模型 (serde)
│   │   │   ├── mod.rs
│   │   │   ├── commit.rs
│   │   │   └── config.rs
│   │   ├── lib.rs
│   │   └── main.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .gitignore
```

## 影响范围

- **全部替换**: v1 的 Python 代码将被完全替换，不做增量迁移
- **保留**: `/arch`, `/design`, `/walkthrough` 文档目录及 `.agents/` 规则
- **Git 历史**: v1 代码在 `main` 分支保留，v2 在 `dev/v2` 分支开发

## 风险

| 风险 | 缓解措施 |
|---|---|
| Node 18 可能不完全支持 Tauri v2 最新特性 | 优先测试兼容性，必要时升级 Node |
| git2 crate 学习曲线 | 先实现最小可用 API（list commits, checkout） |
| React Flow 对大量节点的性能 | 虚拟化 + 懒加载，游戏存档节点量通常 <500 |
