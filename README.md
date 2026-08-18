# 基础设施知识库

把基础设施知识从「人脑 + 群聊 + 零散页面」变成「任务导向、结构化、可被 AI 消费」的知识系统，
并配四个任务型 skill 直接干活。

## 30 秒用法（问 Agent 即可）

| 你说 | Agent 走的路径 |
|---|---|
| 「jaeger 生产实例在哪、谁负责、监控入口？」 | **infra-locate** → 查 `台账/` |
| 「我要给新服务配域名」 | **infra-change** → 找 `手册/域名/`，按 risk 分级执行 |
| 「有台执行机磁盘满了」 | **infra-troubleshoot** → 查 `排障/`，诊断命令直接跑 |
| 「这是我整理的 XX 操作笔记，入库」 | **infra-import** → 分类整理成草稿进 `草稿箱/`，你确认后转正 |

没有 Agent 时直接用引擎：`python scripts/infra.py search <关键词>` / `index` / `lint` / `decay`。

## 目录

| 目录 | 装什么 |
|---|---|
| `台账/` | 资产台账：每个基础设施对象一张 YAML 事实卡（在哪/谁负责/入口/依赖） |
| `手册/` | 操作手册：按**动作**组织（域名申请、证书切换、扩缩容…），带前置/验证/回滚 |
| `排障/` | 排障手册：按**症状**组织（磁盘满、OOM、502、发布失败…），带排查树 |
| `决策/` | 架构决策记录：为什么选它、为什么不选别的 |
| `问答/` | 高频短问答 |
| `架构/` | 拓扑/请求链路/数据流（mermaid） |
| `案例/` | 真实故障复盘（按年） |
| `草稿箱/` | 新知识唯一写入口，人工确认后 git mv 转正 |

## 写入流程

```
python scripts/infra.py new runbook 域名申请绑定 --title "域名申请与绑定"
（AI 或人补内容，套 templates/ 模板；没有的信息写 TODO，禁止编造）
python scripts/infra.py lint                # 零错误才转正
git mv 草稿箱/域名申请绑定.md 手册/域名/ && python scripts/infra.py index
```

## 成熟度与治理

- `draft`（未确认）→ `verified`（`infra.py verify <路径>`）→ `proven`（实战检验，`--proven`）
- 手册/排障半年无引用自动降级（引用靠 `infra.py reference <路径> --in "<场景>"` 记录）
- 台账靠 `last_reviewed` 90 天复审告警；`infra.py decay --fix` 归档闲置草稿（可逆）

## 更多

- Agent 协作契约：[AGENTS.md](AGENTS.md)
- 配置（预算/阈值/lint 规则）：[scripts/infra.json](scripts/infra.json)
- 设计背景：`.background/`（不参与索引）
