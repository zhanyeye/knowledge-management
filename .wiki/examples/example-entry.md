---
id: EXA-001
title: 示例条目——格式速览（不参与索引）
type: 踩坑
maturity: verified
owner: someone
created: 2026-08-16
last_verified: 2026-08-16
last_referenced: null
reference_count: 0
validations: [{by: someone-else, date: 2026-08-16, project: demo}]
source: 示例
tags: [示例, 格式]
related: []
---

# 示例条目——格式速览

> 本文件在 examples/ 下，不被引擎索引。用 `python .wiki/scripts/wiki.py promote --file examples/example-entry.md --to 通用` 可转正体验完整流程。

frontmatter 必填：id / title / type / maturity / owner / created。
其他字段由工作流维护，不要手工改：last_verified、last_referenced、reference_count、validations。

- `type` 六选一：现状 | 决策 | 规范 | 踩坑 | 流程 | 手册（`type add` 可自定义）
- `maturity` 三级：draft → verified → proven（由 /wiki-verify 驱动，不手改）
- `risk`：仅手册类必填 low/medium/high
- `polarity`：仅规范类必填 recommend/avoid

编号 = 分区前缀 + 序号：TEC-001（通用）/ DB-001（基础设施/数据库）/ K8-001（基础设施/k8s）/ PRJ-001（项目）……
正文结构见 `.wiki/templates/<类型>.md`。
