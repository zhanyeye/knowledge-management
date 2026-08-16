---
description: 任务/事故结束后，把值得复用的经验沉淀成 wiki 条目（先进 pending 人审）
argument-hint: "[本次任务或事故简述，可选]"
allowed-tools: Bash(python .wiki/scripts/wiki.py:*), Read, Write, Grep, Glob
---

# 沉淀经验

场景：$ARGUMENTS（为空则回顾当前会话）

1. **筛选**：从会话中提取"下次还会遇到"的知识（宁缺毋滥）：
   - 做了选择、放弃了备选 → 决策
   - 查了半天才发现根因 → 踩坑
   - 提炼出"以后必须/禁止…" → 规范
   - 可复用步骤 → 流程；运维操作 → 手册（评估 risk）
   - 摸清了现状/拓扑 → 现状
2. **查重**：`python .wiki/scripts/wiki.py search <主题> --limit 3`，已有同类条目改为更新原条目。
3. **写入暂存**：候选写到 `pending/<日期-主题>.md`，正文套 `.wiki/templates/<类型>.md` 结构；
   手册类必须含 前置检查/操作步骤/验证/回滚；不确定的步骤写"待专家确认"，禁止编造；内网信息脱敏。
4. **汇报**：列出候选文件与目标分区，人工确认后执行：
   ```bash
   python .wiki/scripts/wiki.py promote --file pending/<文件>.md --to <分区路径>
   ```
5. 若只是沿用了既有知识：不新建，只 `python .wiki/scripts/wiki.py reference <编号> --in "<场景>"`。
