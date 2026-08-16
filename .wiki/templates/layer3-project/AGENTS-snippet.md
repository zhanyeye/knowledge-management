# === 合并进项目根 AGENTS.md / CLAUDE.md ===

## 团队 wiki 协作约定

- 团队 wiki 位置：`WIKI_ROOT=<改为实际路径，如 D:/Workspace/knowledge-management>`
- 动手前：按索引查团队知识（先读 `$WIKI_ROOT/catalog.md`，再读目标目录 catalog.md，按预算读条目全文；预算见 `$WIKI_ROOT/.wiki/config.json` 的 query_budgets）。
- 查到团队知识后，回团队库执行 `python $WIKI_ROOT/.wiki/scripts/wiki.py reference <编号> --in "<项目名>:<任务>"` 记录引用。
- 项目知识写入 `docs/wiki/`；发现跨项目有价值的，晋升到团队 wiki 并在本处留 stub。
- 执行运维手册（手册类条目）前先读全文；`risk: high` 必须人工确认后分步执行。
