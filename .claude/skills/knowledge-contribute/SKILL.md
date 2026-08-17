---
name: knowledge-contribute
description: 完成一次故障处理、技术选型、代码评审、运维操作之后，或用户要求"沉淀知识/记录经验/写入 wiki"时使用。把会话中值得复用的经验提取为条目，先进 pending 暂存，人工确认后转正。
---

# 知识贡献协议

## 什么值得沉淀（宁缺毋滥）

| 信号 | 类型 |
|---|---|
| 做了选择、放弃了备选 | 决策 |
| 查了半天才发现根因 | 踩坑 |
| 提炼出"以后必须/禁止…" | 规范 |
| 可复用的步骤链 | 流程 / 手册（运维操作） |
| 摸清了某系统现状/拓扑 | 现状 |

只是使用了既有知识、没有新发现 → 不新建，只记引用（`wiki.py reference`）。

## 写入规范

1. 先查重：`python .wiki/scripts/wiki.py search <主题> --limit 3`；已有同类 → 建议更新而非新建；
2. 候选写 `pending/<日期-主题>.md`，正文套 `.wiki/templates/<类型>.md`；
3. 手册类必须含：适用场景 / 前置检查 / 操作步骤 / 验证 / 回滚；frontmatter 必填 risk；
4. 不确定的步骤写"待专家确认"，禁止编造命令；内网信息占位符脱敏，凭据不入库。

## 转正与验证

- 人工确认后：`python .wiki/scripts/wiki.py promote --file pending/<文件> --to <分区>`
- 请非作者验证：`/wiki-verify <编号> --by <人> --project <项目>`
- 引用知识：`python .wiki/scripts/wiki.py reference <编号> --in "<场景>"`（写入 `.wiki/logs/refs-*.jsonl`，不改条目文件）

完整契约见 [AGENTS.md](../../../AGENTS.md)。
