---
description: 查询基础设施知识库（定位/排障/答疑）
argument-hint: <问题或症状，如「磁盘满了」「jaeger 谁负责」>
allowed-tools: Read, Grep, Glob, Bash(python .knowhow/knowhow.py:*)
---
# /infra — 查询知识库

用户问题：$ARGUMENTS

按 `.claude/skills/` 的路由规则处理（完整契约见 AGENTS.md）：
- 症状/异常 → **infra-troubleshoot**（先读 问题定位索引.md；未命中再 Grep `knowledge/**/问题定位/`；结论写 reports/）
- 「XX 在哪/谁负责/入口」→ **infra-locate**（域路由表 → Grep/读 `knowledge/<域>/inventory.yaml`）
- 一般知识问题 → 读 INDEX.md → 域 INDEX.md → Grep 关键词 → 按预算读全文

命中并使用知识后必须记引用：
`python .knowhow/knowhow.py reference <路径> --in "<问题摘要>"`
