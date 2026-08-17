---
name: knowledge-query
description: 查询团队 wiki（历史经验、运维手册、规范、决策、踩坑记录）时使用。任何涉及基础设施（数据库/k8s/网络/存储/CI-CD）排障、开发规范、选型决策的任务，动手前先用本技能按索引检索，避免重复踩坑。禁止全文遍历知识库。
---

# 团队 wiki 按需消费协议

完整协作契约见 [AGENTS.md](../../../AGENTS.md)。本 skill 只描述查询动作。

## 触发时机

- 排障任务（现象 → 先查 踩坑/手册）
- 开发/评审任务（先查 规范/决策）
- 执行运维操作（先读对应 手册，并遵守 ops-runbook-guard）

## 空库短路

读 `catalog.md` 后若总条数为 **0**：直接告知空库，建议维护者执行 `/wiki-import <旧文档目录>`，**不要继续读目录索引或 grep 全库**。

## 检索流程（不得跳级、不得遍历）

1. **总目录**：读 `catalog.md` → 定位目标分区
2. **目录索引**：读该目录 `catalog.md`（一行一条）→ 挑出候选
3. **条目全文**：只读预算内条目

## 查询预算（`.wiki/config.json` → `query_budgets`）

| 任务类型 | 目录索引 | 全文条数 | 优先类型 |
|---|---|---|---|
| troubleshoot | ≤2 | ≤3 | 踩坑 → 手册 → 现状 |
| implement | ≤2 | ≤4 | 规范 → 踩坑 → 决策 |
| ops_execute | ≤1 | 1（完整读） | 手册 |
| default | ≤2 | ≤5 | — |

## 引用闭环

命中并使用后：`python .wiki/scripts/wiki.py reference <编号> --in "<任务上下文>"`。
引用写入 `.wiki/logs/refs-YYYY.jsonl`，不改条目文件；decay/stats 从旁路日志聚合。

## 技巧

- `python .wiki/scripts/wiki.py search <关键词> --limit 3` 跨目录定位（含正文/H2/tags）
- `[draft]` 未验证，回答时声明置信度
