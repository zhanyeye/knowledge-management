---
description: 任务/事故结束后，把值得复用的经验沉淀成 wiki 条目（先进 pending 人审）
---

# 沉淀经验

场景：$ARGUMENTS（为空则回顾当前会话）

1. **筛选**（宁缺毋滥）：决策 / 踩坑 / 规范 / 流程 / 手册 / 现状（见 `knowledge-contribute` skill）。
2. **查重**：`python .wiki/scripts/wiki.py search <主题> --limit 3`。
3. **写入暂存**：`pending/<日期-主题>.md`，套 `.wiki/templates/<类型>.md`；手册类含 risk 与 前置检查/验证/回滚。
4. **汇报**：人工确认后 `python .wiki/scripts/wiki.py promote --file pending/<文件>.md --to <分区>`。
5. 仅沿用既有知识：只 `python .wiki/scripts/wiki.py reference <编号> --in "<场景>"`。

完整协作契约见 [AGENTS.md](../../AGENTS.md)。
