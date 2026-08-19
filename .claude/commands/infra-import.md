---
description: 导入/沉淀知识入库（文档、表格、笔记、口述）
argument-hint: <材料路径、粘贴的内容或口述场景>
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python .knowhow/knowhow.py:*)
---
# /infra-import — 导入知识

导入材料：$ARGUMENTS

按 `.claude/skills/infra-import/` 流程执行：
1. 逐条分类（判定表见该 skill；域见 域路由表.yaml）
2. `python .knowhow/knowhow.py new <kind> <中文文件名> --domain <域键> --title "<标题>" --tags "<标签>"` 生成骨架（runbook 对得上产品目录时加 `--subdir`）
3. 原样填入材料中的步骤/参数；**缺的信息写 TODO，禁止编造**；playbook 标 symptoms；资源对象同步补 inventory.yaml
4. `python .knowhow/knowhow.py lint` 错误清零 → `index` 刷新
5. 报告清单（文件/kind/域/遗留 TODO）等用户 review；凭据不入库

量大时分批（每批 ≤10 条）。
