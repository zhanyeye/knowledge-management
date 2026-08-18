# 基础设施知识库 + 自动化

知识按域组织（k8s / 构建资源 / 网络 / 数据库 / 存储…），高频排障与操作逐步
**脚本化（manifest 登记）→ skill 化 → CI 自动化**（L0→L3 四级模型，INDEX.md 有各域自动化仪表盘）。

## 30 秒用法（问 Agent 即可）

| 你说 | Agent 走的路径 |
|---|---|
| 「有台执行机磁盘满了」 | **infra-troubleshoot** → 问题定位索引 → `storage/disk-usage-diagnose` skill（readonly 脚本直接跑） |
| 「我要给新服务配域名」 | **infra-change** → `knowledge/04-网络管理/DNS域名解析/` 手册，三层闸门分级执行 |
| 「jaeger 生产实例在哪、谁负责？」 | **infra-locate** → `knowledge/02-k8s资源管理/inventory.yaml` |
| 「这是我整理的 XX 笔记，入库」 | **infra-import** → 分类写入目标域（draft），lint 后你 review commit |

无 Agent 时直接用引擎：`python scripts/infra.py search 磁盘满` / `index` / `lint` / `decay`。

## 目录

| 位置 | 装什么 |
|---|---|
| `knowledge/00~10-域/` | 每域：`inventory.yaml` 台账 · 操作手册 · `问题定位/` 排障 · `复盘/` · `方案设计/` · `faq.md` |
| `scripts/manifest.yaml` | **脚本注册表**：risk_level（readonly 可直跑 / change 走分级）+ 文档互链，未登记不许执行 |
| `.claude/skills/` | 4 个任务入口 + 各域原子技能（如 `storage/disk-usage-diagnose`） |
| `问题定位索引.md` | 症状 → 域 → 文档 → 脚本 → skill（自动生成） |
| `reports/` | agent 执行留痕（诊断/巡检结论） |
| `INDEX.md` / `域路由表.yaml` | 总索引（含自动化仪表盘）/ agent 寻址表（自动生成） |

## 写入与治理

```
python scripts/infra.py new runbook 域名申请 --domain network   # 直接生成到目标域
（补内容：缺的信息写 TODO 禁止编造；playbook 标 symptoms）
python scripts/infra.py lint        # 零错误后 commit，git diff 即评审
```

成熟度 draft→verified→proven；手册半年无引用自动降级；台账 90 天复审告警；
引用用 `reference` 记录（衰减信号）。详见 [AGENTS.md](AGENTS.md)。

## 下一步（优先补的台账）

26 条手册已就位（owner 待补）。草稿里反复出现「TODO：入口」，本质是缺 inventory——
建议首批补：Rancher 集群 / px+viewpoint / ROMA / HIS / 云龙 / MinIO / 镜像仓 / ELK / Prometheus+Grafana / Jaeger+Pyroscope，
每张回填 `knowledge.*` 链接后，入口类 TODO 大半消灭。
