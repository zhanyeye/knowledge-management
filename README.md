# 基础设施知识库 + 自动化

知识按域组织（k8s / 构建资源 / 网络 / 数据库 / 存储…），高频排障与操作逐步
**脚本化（manifest 登记）→ skill 化 → CI 自动化**（L0→L3 四级模型，INDEX.md 有各域自动化仪表盘）。

## 试用指导（Claude Code）

在本仓库目录下启动 Claude Code（`claude`），用斜杠命令即可完成全部操作：

| 命令 | 用途 | 例子 |
|---|---|---|
| `/infra <问题>` | 查询/排障/定位 | `/infra 有台执行机磁盘满了`<br>`/infra jaeger 生产实例谁负责、监控入口在哪` |
| `/infra-import <材料>` | 导入/沉淀知识 | `/infra-import D:\docs\运维笔记 整理入库`<br>`/infra-import 域名申请流程：先DNS申请，再改nginx配置…` |
| `/infra-exec <意图>` | 按手册执行变更 | `/infra-exec 给新服务 xxx 配内网域名` |

**典型试用流程**（建议按顺序走一遍）：

```
1. 导入：把一批真实文档/笔记丢给 /infra-import
   → agent 逐条分类、生成到 knowledge/<域>/，缺的信息标 TODO（不编造）
   → 输出清单后你看 git diff，满意即提交（commit 就是评审）
2. 查询：/infra 磁盘满了
   → 命中 问题定位索引 → 给排查步骤；配了脚本的会直接跑只读诊断
3. 变更：/infra-exec 我要换证书
   → 找到手册 → 复述前置/步骤/回滚 → 高危操作只给人工指引，不会代跑
4. 沉淀：/infra-import 刚才那个故障记一下：<现象和排查过程>
   → 生成复盘进 复盘/，新根因补进对应 问题定位/ 文档
```

说明：
- 不用命令直接说自然语言也行（skills 会按描述自动触发），命令只是显式入口
- 前提是 Claude Code 在**本仓库目录**启动，才能读到 AGENTS.md 契约和 skills
- 没有 agent 时：`python scripts/infra.py search 磁盘满` / `index` / `lint`

## 目录

| 位置 | 装什么 |
|---|---|
| `knowledge/00~10-域/` | 每域：`inventory.yaml` 台账 · 操作手册 · `问题定位/` 排障 · `复盘/` · `方案设计/` · `faq.md` |
| `scripts/manifest.yaml` | **脚本注册表**：risk_level（readonly 可直跑 / change 走分级）+ 文档互链，未登记不许执行 |
| `.claude/skills/` | 4 个任务入口（locate/change/troubleshoot/import）+ 域原子技能 |
| `.claude/commands/` | 3 个斜杠命令：`/infra` `/infra-import` `/infra-exec`（薄路由，逻辑在 skills） |
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
引用用 `reference` 记录（衰减信号）。凭据/密码禁止入库。详见 [AGENTS.md](AGENTS.md)。

## 首批建议补的台账

知识手册导入后，优先补 inventory（消灭「TODO：入口」）：Rancher 集群 / px+viewpoint /
ROMA / HIS / 云龙 / MinIO / 镜像仓 / ELK / Prometheus+Grafana / Jaeger+Pyroscope，
每张回填 `knowledge.*` 链接。
