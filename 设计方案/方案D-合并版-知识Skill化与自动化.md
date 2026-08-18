# 方案 D：B + C 合并版 —— 以「知识 Skill 化与自动化」为主线

> 状态：**设计方案（未实施）**。合并逻辑：**C 的目录骨架与自动化主干 + B 的治理引擎与结构化台账**。
> C 的域划分来自你们真实文档语料（云龙/门禁Gate/PipelineX/执行资源管理…），直接采用，不再重造。

## 〇、核心主张：知识自动化的四级进化模型

所有「问题定位/操作」类知识按自动化程度分级，**frontmatter 标 `automation` 字段，引擎统计与展示**：

```
L0 文档     人读的排障/操作知识（最低要求：结构化模板 + 台账链接）
L1 脚本化   高频步骤抽成只读脚本，登记进 scripts/manifest.yaml
L2 Skill化 脚本+判读标准+步骤绑定成原子 skill（.claude/skills/<域>/<技能>/）
L3 自动化   CI 定时/告警触发，人只看 reports/ 结论
```

- 每条知识可以停在任意层级，**不强求全部 L3**；高频/高危场景优先推进
- INDEX.md 展示各域自动化率（L0/L1/L2/L3 分布），自动化推进有了可度量的仪表盘
- 这就是「知识 skill 化」的落地路径：不是把文档改写成 skill，而是**让知识沿着 L0→L3 逐级长出执行能力**

## 一、合并取舍表

| 决策点 | 取自 | 理由 |
|---|---|---|
| 目录骨架：单树 `knowledge/NN-域/`，类型作子目录 | C | 贴合真实语料，一个域的东西聚在一起；文档可平移不重写 |
| 域序号（00-10） | C | 人读有顺序感；**agent 寻址不靠编号**，靠生成的域路由表 |
| **manifest.yaml 脚本注册表** | C | 自动化主干：脚本发现/风险分级/文档互链的唯一登记处 |
| **问题定位索引.md（症状→文档→脚本）** | C 概念 + B 实现 | 引擎从 frontmatter **自动生成**，不手工维护、不会腐化 |
| 域路由表.yaml | C 概念 + B 实现 | 引擎从配置生成，agent 优先查它而非记路径 |
| inventory.yaml（每域一份多资源台账） | B | 结构化资产是 locate 类自动化的前提 |
| 治理引擎（三级索引/预算/成熟度/衰减/lint/引用旁车） | B | 知识不腐化的保障；lint 扩展到 manifest 与脚本链接校验 |
| 无草稿箱/无归档目录 | B 后期结论（C 亦无） | 直接写目标位置 + maturity=draft；git 即评审层与历史兜底 |
| 4 个任务入口 skill + 域原子 skill 两层 | B+C | 会话入口（「磁盘满了」）与可执行单元（跑脚本+判读）分工 |
| 文档↔脚本↔manifest 链接校验 | C 概念 + B 实现 | 并入 infra.py lint，单一 CI |
| reports/ 执行留痕 | B+C 合并 | 吸收 C 的 runbooks/history，统一为 reports/（YYYY-MM-主题.md） |
| hooks（pre-apply-guard 等） | C（二期） | Claude Code 下先试，跨工具验证后再定 |
| 方案设计/ 与 SOP 分离 | C | 防 agent 把 RFC 当操作步骤执行；kind 标 adr |
| 根目录 FAQ.md / 常用链接.md | 不取 | 由 INDEX.md + 各域 faq.md + inventory 覆盖，避免三处维护 |

## 二、完整目录树（含真实文件示例）

```
knowledge-management/
│
├── AGENTS.md                        # 唯一契约 + 路由中枢：
│                                    #   症状 → 问题定位索引.md → 域内文档/脚本/skill
│                                    #   变更 → manifest risk_level 分级执行
├── README.md                        # 人的入口（含各域自动化率一览）
├── INDEX.md                         # 【生成】一级索引 + 自动化率仪表盘
├── 问题定位索引.md                   # 【生成】症状关键词 → 域 → 文档 → 脚本 → skill
├── 域路由表.yaml                     # 【生成】domain键 → knowledge/NN-域/ 路径
│
├── knowledge/                       # ═══════ 知识库（按域组织，单树）═══════
│   ├── glossary.md                  # 术语表：黄区/绿区、ROMA、HIS、云龙、px、viewpoint…
│   │
│   ├── 00-通用环境基线/              # kind: reference——只写"我们跟标准 Linux 不同的地方"
│   │   ├── 内部OS与镜像基线.md
│   │   ├── 卷与磁盘挂载规范.md
│   │   └── docker运行时约定.md
│   │
│   ├── 01-镜像制作/
│   │   ├── inventory.yaml           # 镜像仓（harbor）台账
│   │   ├── 统一镜像制作.md           # kind: runbook
│   │   ├── 微服务镜像制作.md
│   │   ├── 镜像仓管理/              # harbor清理.md / 内网下载dockerhub镜像.md
│   │   └── 问题定位/镜像制作常见问题.md   # kind: playbook
│   │
│   ├── 02-k8s资源管理/
│   │   ├── inventory.yaml           # Rancher/各集群台账（入口/负责人/挂哪些业务）
│   │   ├── k8s内部约定.md            # kind: reference（命名/标签规范，非教程）
│   │   ├── 服务器资源/节点资源管理.md
│   │   ├── 可观测/                   # 监控告警.md / 观测组件重启清理.md / 监控看板搭建.md
│   │   ├── 版本发布/                 # 基于Helm的微服务发布部署.md / node-agent发版.md(risk:high)
│   │   ├── 集群管理/                 # 导入集群至Rancher.md / Rancher部署.md
│   │   └── 问题定位/                 # Rancher服务负载查找.md / 微服务重启OOM分析.md / Helm部署失败排查.md
│   │
│   ├── 03-构建资源管理/
│   │   ├── inventory.yaml           # px/viewpoint/ROMA/HIS/云龙/门禁Gate 台账
│   │   ├── ROMA/ HIS/ 云龙/ PipelineX/ 门禁Gate/
│   │   ├── 执行资源管理/             # 执行机新增与换镜像.md / 执行机扩缩容.md /
│   │   │                            # 执行机资源清理.md(risk:high) / 批量VM操作.md(risk:high)
│   │   ├── 复盘/                    # kind: case——gollt时长优化2024.md 等
│   │   └── 问题定位/                 # px执行资源排队问题.md / 执行机残留构建失败.md /
│   │                                # 执行机OOM磁盘满.md / px白名单速度问题.md
│   │
│   ├── 04-网络管理/
│   │   ├── inventory.yaml           # 域名/证书（含到期日!）/nginx/haproxy 实例台账
│   │   ├── architecture.md          # ★ 请求链路图：DNS→代理→ingress→svc
│   │   ├── DNS域名解析/ https证书管理/ 网络防火墙/ 代理网关/
│   │   └── 问题定位/                 # 周边服务变更影响排查.md / 微服务响应时延排查.md
│   │
│   ├── 05-数据库/
│   │   ├── inventory.yaml           # HIS库/自建 mongo/mysql/clickhouse 实例
│   │   ├── HIS数据库/ 自建数据库/
│   │   └── 问题定位/                 # mongo问题.md / 数据库负载分析.md
│   │
│   ├── 06-存储/
│   │   ├── inventory.yaml           # MinIO集群（桶/生命周期）/公共文件服务器
│   │   ├── Minio对象存储/
│   │   └── 问题定位/                 # px公共文件服务器满.md / minio容量inode快满.md
│   │
│   ├── 07-消息中间件/
│   │   ├── inventory.yaml
│   │   └── 问题定位/mq消费延迟问题.md
│   │
│   ├── 08-数据工程与AI平台/
│   │   ├── AI-mlops/ 数据工程/ 数据飞轮/ 特征工程与可视化/
│   │   ├── 方案设计/                # kind: adr——RFC归档，明确"非可执行"
│   │   └── 问题定位/
│   │
│   ├── 09-业务平台对接/              # FOA与珊瑚.md / deployer切换珊瑚指导书.md …
│   └── 10-研发效能与协同/            # AI辅助代码生成.md / 子agent能力验证.md …
│
├── scripts/                         # ═══════ 自动化脚本区 ═══════
│   ├── manifest.yaml                # ★ 脚本注册表（格式见下），lint 校验其一致性
│   ├── infra.py                     # 引擎：index/search/lint/decay/reference/verify/new
│   ├── infra.json                   # 配置：域清单/预算/阈值/lint 规则
│   ├── test_infra.py
│   ├── common/                      # ssh_exec.py / kube_client.py / notify.py（可复用框架）
│   ├── os/                          # install_compiler.sh / disk_cleanup.sh
│   ├── k8s/                         # find_workload_location.sh / diagnose_pod_oom.sh
│   ├── build/                       # px_queue_check.sh / executor_residue_cleanup.sh /
│   │                                # px_low_utilization_finder.py
│   ├── network/                     # cert_rotation.sh
│   ├── db/                          # slow_query_check.py
│   └── storage/                     # disk_usage_scan.sh / minio_lifecycle_config.py
│
├── .claude/skills/                  # ═══════ 技能层 ═══════
│   ├── infra-locate/                # 任务入口（保留）：「XX在哪/谁负责」→ 域 inventory
│   ├── infra-change/                # 「我要做XX」→ 域内 runbook + manifest 分级执行
│   ├── infra-troubleshoot/          # 「XX症状」→ 问题定位索引 → 文档+脚本；结论写 reports/
│   ├── infra-import/                # 「这批笔记入库」→ 直接写目标位置（draft）
│   └── <域>/<技能名>/               # 原子技能（L2）：
│       └── disk-usage-diagnose/     #   SKILL.md（步骤调 scripts/storage/disk_usage_scan.sh）
│           ├── SKILL.md             #   + references/judgment.md（判读标准→链接域内文档）
│           └── references/
│
├── templates/                       # runbook / playbook / case / adr / faq /
│                                    # architecture / inventory / checklist / reference
├── reports/                         # agent 执行留痕 + 巡检报告（YYYY-MM-主题.md）
├── .infra/                          # refs-YYYY.jsonl 引用旁车 + log-YYYY.md
├── .background/
└── .github/workflows/lint.yml       # CI：infra.py lint（含 manifest/链接校验）+ 单测
```

## 三、自动化主干：manifest.yaml（脚本的注册表 + 风险闸门）

```yaml
# scripts/manifest.yaml —— lint 校验：path 存在、related_doc 存在、domain 合法
- name: disk_usage_scan
  domain: storage                    # 域键（对应 域路由表.yaml）
  path: scripts/storage/disk_usage_scan.sh
  description: 分层扫描目录找出磁盘占用最大的文件/目录
  risk_level: readonly               # readonly=agent可直接跑 | change=按手册risk分级
  entry_command: "bash scripts/storage/disk_usage_scan.sh <path> [--depth N]"
  related_doc: knowledge/06-存储/问题定位/px公共文件服务器满.md

- name: executor_residue_cleanup
  domain: build
  path: scripts/build/executor_residue_cleanup.sh
  description: 清理执行机残留数据（先 dry-run）
  risk_level: change                 # change 类必须支持 --dry-run（lint 检查）
  entry_command: "bash scripts/build/executor_residue_cleanup.sh <node> --dry-run"
  related_doc: knowledge/03-构建资源管理/问题定位/执行机残留数据导致构建失败.md
```

**执行规范（AGENTS.md 引用此处）**：
- `risk_level: readonly` → agent 可直接执行（只读诊断）
- `risk_level: change` → 查 related_doc 的 runbook `risk`：medium 逐项确认后执行；high 只出人工指引
- 未登记进 manifest 的脚本视为不存在（agent 不允许凭空跑）

## 四、两张路由表的自动生成（C 的概念 + B 的引擎）

**问题定位索引.md**（`infra.py index` 生成）——数据源是 playbook frontmatter：

```yaml
# knowledge/06-存储/问题定位/px公共文件服务器满.md 的 frontmatter 增加：
symptoms: [磁盘满, inode满, 写文件失败]      # ← 进症状索引
script: scripts/storage/disk_usage_scan.sh   # ← lint 校验已在 manifest 登记
skill: storage/disk-usage-diagnose           # ← 可选，链接原子技能
automation: L2
```

生成结果（人也可读）：

```markdown
| 症状 | 域 | 详细文档 | 脚本 | skill |
|---|---|---|---|---|
| 磁盘满/inode满 | 存储 | knowledge/06-存储/问题定位/….md | disk_usage_scan | storage/disk-usage-diagnose |
| OOM/进程被kill | k8s | knowledge/02-k8s资源管理/问题定位/微服务重启OOM分析.md | diagnose_pod_oom | — |
```

**域路由表.yaml**（同次生成，域清单来自 infra.json）：

```yaml
domains:
  k8s: knowledge/02-k8s资源管理
  build: knowledge/03-构建资源管理
  network: knowledge/04-网络管理
  db: knowledge/05-数据库
  storage: knowledge/06-存储
  mq: knowledge/07-消息中间件
  dataai: knowledge/08-数据工程与AI平台
```

手工维护量为零：症状/脚本/链接全部来自 frontmatter 与 manifest，lint 保证不腐化。

## 五、kind ↔ 位置 ↔ 模板（lint 规则）

| kind | 位置规则 | automation 可取值 |
|---|---|---|
| runbook | `knowledge/NN-域/*.md` 或域内子目录 | L0–L3 |
| playbook | `knowledge/NN-域/问题定位/*.md` | L0–L3 |
| case | `knowledge/NN-域/复盘/*.md` | — |
| adr | `knowledge/NN-域/方案设计/*.md` | —（明确非可执行） |
| reference | `knowledge/NN-域/*.md`（基线/约定） | — |
| registry | `knowledge/NN-域/inventory*.yaml` | — |
| faq | `knowledge/NN-域/faq*.md` | — |
| architecture | `knowledge/NN-域/architecture*.md` | — |

frontmatter 沿用：`title/owner/kind/maturity/risk/tags/related/created/last_verified/last_reviewed`，新增 `automation`（runbook/playbook 适用）与 `symptoms`（playbook 适用）。
三机制不变：三级索引+预算 / 成熟度+衰减 / Lint（扩展 manifest 与脚本链接校验）。

## 六、执行安全（三层闸门叠加）

```
agent 要执行一个动作时：
1. 脚本在 manifest 里吗？        不在 → 不允许凭空跑
2. manifest risk_level？         readonly → 可直接跑
3. change → related_doc 的 risk？  medium → 逐项确认；high → 只出人工指引
```

hooks（二期）：Claude Code 下加 pre-apply-guard.sh 对 change 类二次确认；post-tool-use-log.sh 把执行摘要追加到 reports/。

## 七、迁移映射

**现有 26 条草稿（草稿箱/）→ 新域结构**：

| 草稿 | 新位置 |
|---|---|
| 定位服务部署位置 / node-agent灰度发版 | 02-k8s资源管理/（后者 risk:high） |
| 微服务重启分析 / Helm部署失败 | 02-k8s资源管理/问题定位/ |
| 执行机新增与换镜像 / 执行机扩缩容 / 执行机资源清理 / 批量VM操作 | 03-构建资源管理/执行资源管理/ |
| CI任务排队堆积 / 执行机OOM磁盘满 / 执行机残留构建失败 | 03-构建资源管理/问题定位/ |
| 容器镜像制作 | 01-镜像制作/微服务镜像制作.md |
| RPM安装与yum源 | 00-通用环境基线/ |
| 域名申请绑定 / 客户端证书安装 / 服务端证书切换 / 绿区代理配置 / 防火墙申请 | 04-网络管理/对应子目录/ |
| 变更影响排查 / 微服务时延大 | 04-网络管理/问题定位/ |
| 数据库负载分析 | 05-数据库/问题定位/ |
| 文件服务器磁盘满 / MinIO容量告急 | 06-存储/问题定位/ |
| 观测组件重启清理 / 监控看板搭建 | 02-k8s资源管理/可观测/ |
| HIS凭证获取 | 03-构建资源管理/HIS/ |

**C 方案的真实文档**：目录结构同构，`git mv` 平移即可（去序号叶子名保留语义名）。
**删除**：草稿箱/（含 MANIFEST）、归档/、台账/手册/排障/决策/问答/架构/案例 九分区。
**引擎适配**：kind→位置规则改域制；index 生成三件套（INDEX/问题定位索引/域路由表）；lint 增加 manifest 校验（path/related_doc/domain/dry-run）；new --domain 按域生成。

**首批种子脚本（对准痛点表高频场景，全部 readonly 起步）**：
disk_usage_scan.sh、find_workload_location.sh、diagnose_pod_oom.sh、px_queue_check.sh
——各配 1 条 问题定位 文档（symptoms/script/automation:L1），其中 disk_usage_scan 进一步做成 L2 原子 skill 示范（storage/disk-usage-diagnose）。

## 八、实施顺序与验收

1. 目录重建 + 26 条草稿迁移 + manifest/路由三件套生成逻辑
2. 引擎适配（kind 规则/lint 扩展/automation 统计）+ 首批 4 个种子脚本 + 1 个 L2 skill 示范
3. 单测改写跑通 + CI workflow
4. AGENTS.md（路由+三层闸门）/ README / 四 skill 更新
5. 全链路冒烟 → 单 commit

**验收**：
- 单测全过；lint 零错误（含 manifest 校验）
- `问题定位索引.md` 生成且症状→文档→脚本链路可点
- `search 磁盘满` 命中 06-存储/问题定位/，且能顺着 manifest 找到 disk_usage_scan.sh 跑通（本机可测的只读部分）
- INDEX.md 展示各域 automation 分布（L0×26 起步）
- 你提供 C 的真实文档后可整体平移（结构同构，无需改写）
