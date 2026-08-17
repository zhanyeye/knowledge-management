---
description: 查团队 wiki（排障/规范/手册/历史决策），自动按预算检索
---

# 查 wiki

用户问题：$ARGUMENTS

流程（不要遍历全库）：

1. **空库短路**：读 `catalog.md`；若总条数为 0，直接告知空库并建议 `/wiki-import <旧文档目录>`，**不要空转三级索引**。
2. **判断任务类型**：troubleshoot / implement / ops_execute / default，预算见 `.wiki/config.json` → `query_budgets`。
3. **总目录**：从 `catalog.md` 选出最相关目录；拿不准时先跑 `python .wiki/scripts/wiki.py search $ARGUMENTS --limit 3`（检索含正文）。
4. **目录索引**：读选中目录的 `catalog.md`，挑最相关的几条。
5. **条目全文**：只读预算内的条目。`risk: high` 的手册必须先读前置检查并要求人工确认。
6. **记引用**：回答中标注来源编号；完成后执行 `python .wiki/scripts/wiki.py reference <编号> --in "$ARGUMENTS"`（写入 `.wiki/logs/refs-*.jsonl`，不改条目文件）。

## 输出要求

- 先给结论再给依据，标注来源编号与置信度（`[draft]` / `[verified]` / `[proven]`）。
- 库里没有相关知识时直说，并建议用户事后 `/wiki-save` 沉淀。

完整协作契约见 [AGENTS.md](../../AGENTS.md)。
