---
name: infra-import
description: 知识导入与整理入库。当用户提供文档/表格/笔记/口述场景要沉淀进知识库时使用，如「把这些运维笔记整理入库」「这是我们的域名申请流程」。AI 分类、直接写目标域（draft），lint 后人工 review commit。
---

# infra-import — 导入整理

把原始材料（文档/表格/聊天记录/口述）变成结构化知识。

## 流程

### 1. 理解材料，逐条分类

一条「场景」一个文件。按 AGENTS.md 判定表分类（域见 域路由表.yaml）：

| 材料特征 | kind → 位置 |
|---|---|
| 对象的事实（实例/集群/域名/证书/平台） | registry → 域内 `inventory.yaml` 追加资源 |
| 一个动作怎么做（申请/配置/扩容/发版） | runbook → 域顶层或子目录 |
| 一个症状怎么查 | playbook → 域内 `问题定位/` |
| 选型/设计理由/RFC | adr → 域内 `方案设计/` |
| 短问答 | faq → 域内 `faq-*.md` |
| 链路/拓扑 | architecture → 域内 `architecture-*.md` |
| 真实故障复盘 | case → 域内 `复盘/` |
| 内部约定/基线（只写与通用标准的不同处） | reference → 域顶层 |

材料是混合体时拆成多条，互相用 `related` 链接。

### 2. 生成与填充

```bash
python .knowhow/knowhow.py new <kind> <中文文件名> --domain <域键> --title "<中文标题>" --tags "<逗号分隔>"
# runbook/reference 对得上产品子目录时加上，例如：
#   --subdir DNS域名解析
# playbook/case/adr/registry 不要加 --subdir
```

填充规则：
- **原始材料里的步骤/参数原样保留**；材料没有的信息（前置/验证/回滚/负责人）写 `TODO`，**禁止编造**
- playbook 评估 risk 并标 `symptoms`；runbook/playbook 标 `automation: L0`
- 涉及资源对象 → 同步补 `inventory.yaml`，两边 knowledge/related 互链
- 高频动作里有可脚本化的只读步骤 → 顺手 L1 化（写脚本登记 manifest，related_doc 指回文档）

### 3. 校验与交付

```bash
python .knowhow/knowhow.py lint    # 错误清零（TODO 不算错误）
python .knowhow/knowhow.py index   # 刷新索引三件套
```

向用户报告：每条「文件 → kind/域 → 遗留 TODO」，等 review。git diff/commit 即评审，无暂存区。

### 4. 批量导入（如痛点场景表）

表格逐行处理：一行=一个场景=一个文件；「问题/场景」列做标题与 tags，「当前步骤」列填进排查路径/操作步骤。
量大分批交付（每批 ≤10 条）。
