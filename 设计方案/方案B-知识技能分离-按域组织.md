# 方案 B：知识与技能分离 · 按域组织

> 状态：**设计方案（未实施）**。参考「知识分层、技能原子化、脚本可执行、清单结构化」的思路，
> 结合本仓 `.background/` 专家方案与痛点场景表设计。与方案 A（当前已实现的七分区类型制）对比见 `方案A-*.md` 文末。

## 一、设计原则与取舍

**采纳**：
1. 知识与技能分离：`knowledge/` 存「是什么/为什么」，`runbooks/` 存「怎么做」，`.claude/skills/` 是可执行封装
2. **按领域组织**（k8s/ci/network/…）：贴合「我有个 Mongo 问题」的思维习惯，一个域的东西聚在一起
3. `inventory.yaml` 结构化清单：每域一份台账，agent/脚本可直接 parse（比自然语言文档检索命中率高）
4. 原子 skill 带 `scripts/`：技能只做一件事，复杂逻辑下沉脚本，可独立 CLI 运行、可被 CI 调用
5. `reports/` 执行留痕：排障结论落盘，形成闭环
6. CI（lint + 单测）、术语表 glossary

**不采纳/缓建**：
- `.claude/agents/` 子代理 —— 当前 4 个任务 skill 够用，原子 skill 多了再说
- `.claude/hooks/` —— 跨工具（Cursor/ZCode）兼容不确定；引用闭环已有 `.infra/refs` 轻量版
- `configs/` 配置基线 —— 暂无真实内容，有了再建
- `daily-inventory-sync` CI —— 需要集群访问权限，二期
- **草稿箱/归档目录** —— 直接写目标分区，`maturity: draft` 就是「未确认」标签，git diff/commit 就是评审层；
  decay 只降级 + 报「建议删除」清单，删除由人执行、git 历史兜底

**命名**：英文骨架 + 中文内容（FAQ/ADR/runbook 是行业通用词，专家方案本身就用这套）。

## 二、完整目录树（含真实文件示例）

```
knowledge-management/
│
├── AGENTS.md                       # 唯一契约 + 路由中枢：
│                                   #   遇到问题 → 有无原子skill(.claude/skills/) → 查 runbooks/域/
│                                   #   → 查 knowledge/域/ → 查 incidents/ → 事后沉淀新知识
├── README.md                       # 人的入口：30秒用法 / 目录表 / 下一步（先补哪些 inventory）
├── INDEX.md                        # 一级索引【自动生成】三级检索: INDEX → 域INDEX → 条目全文
│
├── knowledge/                      # ── 事实层：是什么 / 为什么（人读为主，skill 引用）──
│   │
│   ├── glossary.md                 # 术语表：黄区/绿区/通用区、ROMA、HIS、EKS、Helm-CD、px、
│   │                               #   viewpoint、node-agent…（词条名来自现有文档，释义待补）
│   │
│   ├── k8s/                        # Rancher/集群/负载/node-agent
│   │   ├── inventory.yaml          # ★ 集群台账：每集群一条（入口/负责人/挂哪些业务/版本）
│   │   ├── architecture.md         # 集群拓扑与命名空间规划（mermaid）
│   │   ├── conventions.md          # 命名/标签规范（选配）
│   │   ├── faq.md                  # 域 FAQ（选配）
│   │   └── incidents/              # 该域故障复盘（选配，按年命名 2026-xx-xxx.md）
│   │
│   ├── ci/                         # px 流水线 / 执行机 / 镜像 / 发布链路
│   │   ├── inventory.yaml          # ★ px 平台、viewpoint、镜像仓、执行机池
│   │   └── architecture.md         # 构建链路图：代码仓→流水线→执行机→镜像仓→Helm发布
│   │
│   ├── vm/                         # 虚机资源
│   │   ├── inventory.yaml          # ★ 虚机台账（低利用率机/执行机/公共服务器分组）
│   │   └── architecture.md         # 网络区分布：黄区/绿区/通用区（选配）
│   │
│   ├── network/                    # 域名 / 证书 / 代理 / 防火墙
│   │   ├── inventory.yaml          # ★ 域名、证书、nginx/haproxy 实例台账（含到期日字段）
│   │   ├── architecture.md         # ★ 请求链路图：DNS→代理→ingress→svc（排障"因果链"的载体）
│   │   └── faq.md
│   │
│   ├── database/
│   │   ├── inventory.yaml          # ★ HIS 库、自建 mongo/mysql/clickhouse 实例
│   │   └── architecture.md         # Mongo ETL→ClickHouse 数据流（选配）
│   │
│   ├── middleware/
│   │   └── inventory.yaml          # ★ redis / nsq / kafka 实例
│   │
│   ├── storage/
│   │   ├── inventory.yaml          # ★ MinIO 集群（桶清单/生命周期）、公共文件服务器
│   │   └── architecture.md         # 桶规划与容量策略（选配）
│   │
│   ├── observability/
│   │   ├── inventory.yaml          # ★ prometheus/grafana/jaeger/pyroscope/elk：入口+数据目录+保留策略
│   │   └── architecture.md         # 指标/日志/trace 三条数据流（选配）
│   │
│   └── platforms/
│       ├── inventory.yaml          # ★ HIS/ROMA/viewpoint/harbor/mirrors 平台账
│       └── faq.md                  # 「his 的 appkey 去哪拿」类短问答
│
├── runbooks/                       # ── 程序层：怎么做（操作手册 + 排障手册混排，frontmatter kind 区分）──
│   ├── k8s/
│   │   ├── 定位服务部署位置.md      # kind: runbook
│   │   ├── node-agent灰度发版.md    # kind: runbook, risk: high
│   │   └── 微服务重启分析.md        # kind: playbook（按症状）
│   ├── ci/
│   │   ├── Helm部署失败.md          # playbook
│   │   ├── CI任务排队堆积.md        # playbook
│   │   ├── 执行机OOM磁盘满.md       # playbook
│   │   ├── 执行机残留构建失败.md    # playbook
│   │   ├── 执行机新增与换镜像.md    # runbook
│   │   ├── 执行机扩缩容.md          # runbook
│   │   ├── 执行机资源清理.md        # runbook, risk: high
│   │   └── 容器镜像制作.md          # runbook
│   ├── vm/
│   │   ├── RPM安装与yum源.md        # runbook
│   │   └── 批量VM操作.md            # runbook, risk: high
│   ├── network/
│   │   ├── 域名申请绑定.md          # runbook
│   │   ├── 绿区代理配置.md          # runbook, risk: high
│   │   ├── 客户端证书安装.md        # runbook
│   │   ├── 服务端证书切换.md        # runbook, risk: high
│   │   ├── 变更影响排查.md          # runbook
│   │   ├── 防火墙申请.md            # runbook
│   │   └── 微服务时延大.md          # playbook
│   ├── database/
│   │   └── 数据库负载分析.md        # playbook
│   ├── storage/
│   │   ├── 文件服务器磁盘满.md      # playbook
│   │   └── MinIO容量告急.md         # playbook
│   ├── observability/
│   │   ├── 观测组件重启清理.md      # runbook, risk: high
│   │   └── 监控看板搭建.md          # runbook
│   └── platforms/
│       └── HIS凭证获取.md           # runbook
│
├── adr/                             # ── 决策记录（跨域，编号连续）──
│   ├── INDEX.md                     # 【自动生成】
│   └── 0001-自研haproxy代替ALB.md   # 例（待写；专家方案给了首批5条建议）
│
├── templates/                       # 模板（infra.py new 按此生成）
│   ├── runbook.md                   # 操作手册：目标/前置/步骤/验证/回滚/常见问题/关联
│   ├── playbook.md                  # 排障手册：症状/排查树/常见根因/升级条件
│   ├── incident-case.md             # 故障复盘：现象/时间线/根因/修复/改进
│   ├── adr.md                       # 背景/决策/备选/影响/约束
│   ├── faq.md                       # 问答组
│   ├── architecture.md              # 架构说明（mermaid 必带）
│   ├── inventory.yaml               # 域台账模板（一文件多资源，见下）
│   └── checklist.md                 # 轻量检查清单（runbook 变体）
│
├── scripts/
│   ├── infra.py                     # 引擎：index / search / lint / decay / reference / verify / new
│   ├── infra.json                   # 配置：查询预算 / 衰减阈值 / lint 规则
│   └── test_infra.py                # 单测
│
├── reports/                         # agent 执行留痕（infra-troubleshoot 结论落盘）
│   └── 2026-08-磁盘满-公共文件服务器.md   # 命名：YYYY-MM-<主题>.md
│
├── .claude/skills/                  # 任务入口（保留4个）+ 原子skill模式（新增）
│   ├── infra-locate/SKILL.md        # 「XX在哪/谁负责」→ 查 knowledge/*/inventory.yaml
│   ├── infra-change/SKILL.md        # 「我要做XX」→ runbooks/域/ 手册 + risk 分级执行
│   ├── infra-troubleshoot/SKILL.md  # 「XX症状」→ runbooks/域/ playbook + 结论写 reports/
│   ├── infra-import/SKILL.md        # 「这批笔记入库」→ 分类整理直接写目标位置（draft）
│   └── disk-usage-diagnose/         # ★ 原子 skill 种子（文档 skill 化自动化的模式样板）
│       ├── SKILL.md                 #   何时用：磁盘告警/写满，先跑脚本拿画像再对照判读
│       ├── scripts/diagnose.sh      #   只读诊断：df -h + du 逐层下钻 top-N（可独立 CLI 运行）
│       └── references/judgment.md   #   判读标准（引用 knowledge/storage/ 的台账与策略）
│
├── .infra/                          # refs-YYYY.jsonl 引用旁车 + log-YYYY.md 操作日志
├── .background/                     # 设计资料（不参与索引）
└── .github/workflows/lint.yml       # CI：push/PR 跑 python scripts/infra.py lint + 单测
```

★ = 该域建议优先补的文件（检索命中率最高的位置）。

## 三、inventory.yaml 格式（每域一份，一文件多资源）

```yaml
# knowledge/platforms/inventory.yaml
resources:
  - resource_type: platform          # platform|cluster|database|middleware|domain|certificate|storage|vm|service
    name: his
    display_name: HIS 平台
    env: prod
    criticality: high
    owner: {team: "", primary: ""}   # TODO
    entrypoints: {console: "TODO", dashboard: ""}
    knowledge:                       # 跨文件关联唯一源，lint 校验链接存在
      runbooks: [runbooks/platforms/HIS凭证获取.md]
      faqs: [knowledge/platforms/faq.md]
    last_reviewed: "2026-08-18"      # 超90天 lint 告警
  - resource_type: platform
    name: roma
    ...
```

## 四、条目 frontmatter（沿用现行）

`title / owner / kind / maturity(draft|verified|proven) / risk / tags / related / created / last_verified / last_reviewed`
路径即 ID；目录英文、文件名中文（产品名保留英文）。

## 五、关键规则

- **写入**：直接写目标位置（无草稿箱），maturity 必须为 draft；
  `python scripts/infra.py new <kind> <名> --domain <域>` 生成骨架；lint 零错误后 commit，git diff/PR 即人审
- **kind↔位置校验**（lint）：runbook/playbook→`runbooks/`；registry→`inventory*.yaml`；faq→`faq*.md`；
  architecture→`architecture*.md`；case→`incidents/`；adr→`adr/NNNN-*`
- **衰减**：手册/排障 6 个月无引用信号自动降级（decay 仅报告，无归档目录）；台账走 last_reviewed 90 天告警
- **三机制保留**：三级索引+查询预算 / 三级成熟度+衰减 / Lint
- **risk 分级执行**：low 只读诊断直接跑 / medium 逐项确认 / high 只出人工指引

## 六、迁移映射（现状 26 条草稿 → 新结构）

| 现草稿（草稿箱/） | 新位置 | kind |
|---|---|---|
| 定位服务部署位置 / node-agent灰度发版 / 微服务重启分析 | runbooks/k8s/ | runbook / runbook / playbook |
| Helm部署失败 / CI任务排队堆积 / 执行机OOM磁盘满 / 执行机残留构建失败 / 执行机新增与换镜像 / 执行机扩缩容 / 执行机资源清理 / 容器镜像制作 | runbooks/ci/ | 前4为 playbook，后4为 runbook |
| RPM安装与yum源 / 批量VM操作 | runbooks/vm/ | runbook |
| 域名申请绑定 / 绿区代理配置 / 客户端证书安装 / 服务端证书切换 / 变更影响排查 / 防火墙申请 / 微服务时延大 | runbooks/network/ | 前6为 runbook，时延大为 playbook |
| 数据库负载分析 | runbooks/database/ | playbook |
| 文件服务器磁盘满 / MinIO容量告急 | runbooks/storage/ | playbook |
| 观测组件重启清理 / 监控看板搭建 | runbooks/observability/ | runbook |
| HIS凭证获取 | runbooks/platforms/ | runbook |

删除：草稿箱/（含 MANIFEST.md，其「首批补 10 张 inventory」建议并入 README）、归档/、
台账/手册/排障/决策/问答/架构/案例 九个旧中文分区。引擎删除 inbox/archive 特殊逻辑，decay 移除 --fix。

## 七、实施顺序与验收

1. 目录重建 + 26 条迁移（Python 脚本，防 Windows 编码问题）
2. 引擎适配（kind→顶层映射、文件名 lint 规则、new --domain）+ 模板改造 + glossary / 原子 skill / CI
3. 单测改写跑通
4. AGENTS/README/四 skill 更新
5. lint/index/search/reference/decay 全链路冒烟 → 单 commit

验收：单测全过；lint 零错误；INDEX 三级可用；`search 磁盘` 命中 runbooks/storage/；旧目录无残留。
