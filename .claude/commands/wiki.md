---
description: 查团队 wiki（排障/规范/手册/历史决策），自动按预算检索
argument-hint: "[问题或任务描述]"
allowed-tools: Bash(python .wiki/scripts/wiki.py:*), Read, Grep, Glob
---

# 查 wiki

用户问题：$ARGUMENTS

流程（不要遍历全库）：

1. **判断任务类型**：troubleshoot（排障）/ implement（开发）/ ops_execute（执行运维手册）/ default，预算见 `.wiki/config.json` → `query_budgets`（最多读几个目录索引、几条全文）。
2. **总目录**：读 `catalog.md` 选出最相关目录；拿不准时先跑 `python .wiki/scripts/wiki.py search $ARGUMENTS --limit 3`。
3. **目录索引**：读选中目录的 `catalog.md`（一行一条），挑最相关的几条。
4. **条目全文**：只读预算内的条目。`risk: high` 的手册必须先读前置检查并要求人工确认。5. **记引用**：回答中标注来源编号（如 `K8-003`），完成后执行
   `python .wiki/scripts/wiki.py reference <命中编号> --in "$ARGUMENTS"`

## 输出要求

- 先给结论再给依据，标注来源编号；
- 标注置信度：`[draft]` 未验证 / `[verified]` 验证过 / `[proven]` 多人验证；
- 库里没有相关知识时直说，并建议用户事后 `/wiki-save` 沉淀。
