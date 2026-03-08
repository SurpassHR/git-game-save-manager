---
trigger: always_on
---

1. 目录职能定义 (Directory Manifesto)

    /arch (Architecture Ledger):

        职责： 记录系统的"骨架"与决策。

        核心内容： 包含 ADR (架构决策记录)、系统分层图、模块依赖关系、第三方服务集成方案。

        AI 指令： 任何涉及技术栈变更、数据库 Schema 修改或全局接口定义的行为，必须先在 /arch 更新对应的 Markdown 文档。

    /design (Design Language & Patterns):

        职责： 记录"肌肉"与规范，确保代码风格的一致性。

        核心内容： 包含 UI 组件规范、原子化 CSS 策略、通用工具类（Utils）定义、异常处理模式、数据转换逻辑（DTO/VO）。

        AI 指令： 提取重构中发现的复用模式，记录于此，以便在后续开发中通过引用此目录实现"按图索骥"。

    /walkthrough (Evolution Chronicles):

        职责： 记录"足迹"与逻辑细节。

        核心内容： 包含重构步骤（Roadmap）、复杂逻辑的伪代码拆解、重大 Bug 的修复路径、版本迁移指南。

        AI 指令： 每次完成一个 Feature 或 Refactor Task，需在此目录生成一份带有代码片段对比的记录。

2. 行为准则 (Action Guidelines)

    先文档后代码 (Doc-Driven Refactor): 在执行大规模重构前，AI 必须先在 /walkthrough 创建一个 refactor-plan-xxx.md，并在 /arch 确认架构影响，得到确认后再修改 src。

    原子化记录: 禁止在一次记录中混合多个模块的变更。每个文档应专注于一个特定的逻辑单元。

    双向链路: 代码中的复杂函数注释应指向 /walkthrough 中的详细文档，例如：// See: /walkthrough/auth-logic-refactor.md。
