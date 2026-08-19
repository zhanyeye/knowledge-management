---
name: infra-change
description: 基础设施变更指引与执行。当用户说「我要做 XX」时使用：配域名、换证书、开通防火墙、扩缩容、新增执行机、接入监控、批量操作等。找域内手册并按三层闸门执行。
---

# infra-change — 变更指引

「这件事怎么做、做错了怎么回」。

## 流程

1. 找手册（**Grep / 读索引，不要用 knowhow.py 检索**）：
   - 能定域 → 读 `knowledge/<域>/INDEX.md`
   - Grep frontmatter `kind: runbook`，加上动作关键词（域名/证书/扩容…）
   - 域名/证书类多在 `knowledge/04-网络管理/` 对应子目录
2. 列出候选后**确认一篇**，完整读全文（预算 1 条，不截断），向用户复述：前置条件 → 步骤 → 验证 → 回滚。
3. 涉及的资源先 `infra-locate` 查 inventory（环境/入口/负责人），避免在错误对象上操作。
4. 执行（见三层闸门）。每步做完先验证再进下一步。
5. 收尾：`reference <手册路径> --in "<变更内容>"`；手册有误/缺节 → 直接修订（lint 后提交）。

## 三层闸门（AGENTS.md 第四节）

1. 要跑的脚本**必须在 scripts/manifest.yaml 登记**——未登记的脚本一律不执行
2. manifest `risk_level: readonly` → 可直接执行
3. `change` → 查手册 frontmatter `risk`：**medium** 展示完整步骤清单逐项确认后执行；**high**（证书切换/批量主机/删数据/核心发版）只输出人工执行指引，不代跑

## 没有手册时

Grep 与域 INDEX 都未命中，才视为没有手册。不要把一次关键词落空当成库里没有。

不要凭通用知识直接在生产上操作：
1. 从用户/已有文档收集步骤，`python .knowhow/knowhow.py new runbook <名> --domain <域>` 落骨架；
2. 用户确认步骤无误后按闸门执行；
3. 执行验证后 `verify` 升级，下次就有手册了。高频动作顺势 L1 化：步骤抽成脚本登记 manifest。
