---
description: 按手册执行基础设施变更（三层闸门分级）
argument-hint: <要做的事，如「给新服务配域名」「扩容执行机」>
allowed-tools: Read, Grep, Glob, Bash(python .knowhow/knowhow.py:*), Bash(bash scripts/*:*)
---
# /infra-exec — 执行变更

变更意图：$ARGUMENTS

按 `.claude/skills/infra-change/` 流程执行：
1. 读域 INDEX.md；Grep frontmatter `kind: runbook` + 动作关键词。确认一篇后**完整读全文**
2. 资源先查 inventory（infra-locate 规则），复述：前置 → 步骤 → 验证 → 回滚
3. 三层闸门：脚本必须在 scripts/manifest.yaml 登记；readonly 可直跑；change 按手册 risk（medium 逐项确认 / high 只出人工指引）
4. 收尾：`reference <手册路径> --in "<变更内容>"`；手册有误顺手修订
5. Grep 未命中才视为没有手册，禁止把一次落空当成库里没有
