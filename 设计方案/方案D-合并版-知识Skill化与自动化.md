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
——各配 1 条 问题定位 文档（symptoms/script/automation:L1），其中 disk_usage_scan 完整做成 **L2 原子 skill 示范（见「九、种子 Skill 全文示例」）**。

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
- **种子 skill 端到端演示通过**：按「九」的 SKILL.md 走一遍诊断流程（本地目录模拟目标机）
- 你提供 C 的真实文档后可整体平移（结构同构，无需改写）

## 九、种子 Skill 全文示例：storage/disk-usage-diagnose（L2 示范）

> 这是「知识 skill 化」的标准样板：**SKILL.md（流程）+ script（能力）+ references（判读知识）** 三件套，
> 通过 manifest 与 问题定位文档 双向互链。照此模式复制即可批量产出原子技能。

### 9.1 目录与互链关系

```
.claude/skills/storage/disk-usage-diagnose/
├── SKILL.md                     # 流程（何时用/步骤/输出/升级）
└── references/
    └── judgment.md              # 判读知识（引用域内文档，不复制内容）

scripts/storage/disk_usage_scan.sh    # 能力（manifest 登记，readonly）
knowledge/06-存储/问题定位/px公共文件服务器满.md   # 知识源头（symptoms/skill 字段回链）
```

### 9.2 SKILL.md（全文）

```markdown
---
name: disk-usage-diagnose
description: 磁盘/inode 告警或写满时的只读诊断。输入目标主机，输出占用画像、
  疑似根因与处理建议（不执行清理）。当用户说「磁盘满了 / inode 满了 / no space left /
  写文件失败」或收到存储容量告警时使用。
---

# 磁盘占用诊断（只读）

## 何时使用
- 监控告警磁盘或 inode 使用率超阈值
- 应用报 No space left on device / 写文件失败
- 执行机 / 公共文件服务器 / MinIO 宿主机疑似写满

## 前置确认（动手前必查）
1. 目标主机与疑似路径；不知道路径先查 knowledge/06-存储/inventory.yaml
   （或 03-构建资源管理/inventory.yaml 执行机池），用 infra-locate 定位
2. 只需要只读登录权限
3. 本技能只诊断不清理：任何清理/删除动作转 infra-change 走对应手册（risk 分级）

## 步骤
1. 整体画像（标出超 85% 的挂载点，含 inode）：
   bash scripts/storage/disk_usage_scan.sh <host> --quick
2. 对每个超阈值挂载点下钻两层，取 TOP 占用：
   bash scripts/storage/disk_usage_scan.sh <host> --path <挂载点> --depth 2
3. 按 references/judgment.md 的模式表判读：
   - 命中「已知可清理模式」→ 给出建议命令（一律带 --dry-run），交人工或 infra-change 确认执行
   - 未命中/未知大目录 → 报告路径+大小+属主线索，查 inventory 定位资源 owner
4. 收尾两件事：
   - 结论写 reports/YYYY-MM-磁盘诊断-<host>.md
   - python scripts/infra.py reference knowledge/06-存储/问题定位/px公共文件服务器满.md --in "<简述>"

## 输出格式
- <host> 磁盘画像（df -h / df -i，超阈值项加标）
- TOP 占用目录（大小 + 最后修改时间线索）
- 疑似根因（按 judgment.md 模式编号）+ 置信度
- 建议动作清单（readonly=已执行；change=待人工确认，逐条附命令）

## 升级条件
- df 满但 du 找不到大文件 → 已删除文件被进程持有（judgment.md 模式 E），需重启持有进程
- 涉及生产数据删除 → 一律人工，本技能止步于建议
- MinIO 对象存储容量问题 → 转其容量 playbook（生命周期策略路径不同）
```

### 9.3 scripts/storage/disk_usage_scan.sh（全文，readonly）

```bash
#!/usr/bin/env bash
# 磁盘占用只读扫描 —— manifest 登记: disk_usage_scan / risk_level: readonly
# 用法:
#   disk_usage_scan.sh <host> --quick                     # df 画像，标出超阈值挂载点
#   disk_usage_scan.sh <host> --path <dir> [--depth N]    # 逐层 du 下钻 TOP20
# 说明: 仅执行 df/du 只读命令，不做任何变更；host 为本机时可用 local 代替。
set -euo pipefail

HOST="${1:?用法: $0 <host> (--quick | --path <dir>) [--depth N] [--threshold P]}"
THRESH=85
DEPTH=2
MODE=""
DIR=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --quick)     MODE="quick" ;;
    --path)      MODE="path"; DIR="${2:?--path 需要目录参数}"; shift ;;
    --depth)     DEPTH="$2";   shift ;;
    --threshold) THRESH="$2";  shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$MODE" ] || { echo "必须指定 --quick 或 --path <dir>" >&2; exit 2; }

run() {  # host=local 时本机执行，否则 ssh
  if [ "$HOST" = "local" ]; then bash -c "$1"; else ssh -o BatchMode=yes "$HOST" "$1"; fi
}

case "$MODE" in
  quick)
    echo "== df -h（标出使用率>${THRESH}%） =="
    run "df -hP | awk -v t=$THRESH 'NR==1 || substr(\$5,1,length(\$5)-1)+0>t'"
    echo; echo "== df -i（inode，标出使用率>${THRESH}%） =="
    run "df -iP | awk -v t=$THRESH 'NR==1 || substr(\$5,1,length(\$5)-1)+0>t'"
    echo; echo "== 全量 df -h =="; run "df -h"
    ;;
  path)
    echo "== du 下钻 $DIR (depth=$DEPTH, TOP20) =="
    run "du -h --max-depth=$DEPTH '$DIR' 2>/dev/null | sort -rh | head -20"
    ;;
  *) echo "内部错误: 未知模式 $MODE" >&2; exit 2 ;;
esac
```

### 9.4 references/judgment.md（全文要点）

```markdown
# 磁盘占用判读标准（只读诊断的"大脑"）

| 模式 | 特征 | 确认命令（readonly） | 处置方向 |
|---|---|---|---|
| A 日志堆积 | /var/log、应用 logs 目录占比大，文件按天滚动未清理 | ls -lh <dir>; du -sh <dir> | 配置轮转/压缩归档；清理走手册 |
| B docker 膨胀 | /var/lib/docker 大 | docker system df | prune 建议（change，人工确认） |
| C 构建残留 | 执行机 /tmp、工作目录脏数据 | du --max-depth=1 /tmp | 链 03/问题定位/执行机残留构建失败.md |
| D 海量小文件 inode 满 | df -i 满而 df -h 不满 | df -i; find <dir> -type f \| wc -l | 定位小文件目录（minio 对象/队列） |
| E 幽灵占用 | df 满但 du 总和对不上 | lsof +L1 或 lsof \| grep deleted | 重启持有进程（change，人工） |
| F 保留块 | ext4 默认保留 5%，非 root 可写满 | tune2fs -l <dev> \| grep -i reserved | 评估调低保留比例（change） |

判读原则：命中 A–D 给出 dry-run 建议；E/F 先报告证据链再谈处置；
任何生产数据删除一律人工。owner 未知的目录先查 knowledge/*/inventory.yaml。
```

### 9.5 接线（manifest + 问题定位文档 frontmatter）

```yaml
# scripts/manifest.yaml 追加
- name: disk_usage_scan
  domain: storage
  path: scripts/storage/disk_usage_scan.sh
  description: 分层扫描目录找出磁盘/inode 占用（只读）
  risk_level: readonly
  entry_command: "bash scripts/storage/disk_usage_scan.sh <host> --quick"
  related_doc: knowledge/06-存储/问题定位/px公共文件服务器满.md
```

```yaml
# knowledge/06-存储/问题定位/px公共文件服务器满.md 的 frontmatter
symptoms: [磁盘满, inode满, no space left, 写文件失败]
script: scripts/storage/disk_usage_scan.sh
skill: storage/disk-usage-diagnose
automation: L2
```

→ `infra.py index` 自动把它写进 问题定位索引.md；lint 校验 script 已登记、
skill 目录存在；INDEX.md 的 storage 域自动化率出现首个 L2。

## 十、原子 Skill 编写规范（L2 验收清单）

新技能合入前逐条自检（lint 能查的查 lint，查不了的走 review）：

1. **单一职责**：一个技能只解决一类症状/动作；跨域内容放 references 引用，不复制
2. **只读优先**：脚本默认 readonly；确需变更则拆「诊断(readonly) + 处置(change 手册)」两段
3. **change 必带 dry-run**：manifest 里 risk_level: change 的脚本必须支持 --dry-run（lint 检查）
4. **登记才可执行**：脚本必须进 manifest 且 related_doc 指回知识文档；无登记=不存在
5. **知识不搬家**：判读/背景知识写在 references/ 并链接域内文档，SKILL.md 只写流程，≤200 行
6. **留痕闭环**：执行后写 reports/ + `infra.py reference` 记引用（衰减机制靠它）
7. **命名**：`.claude/skills/<域>/<动词-对象>/`，英文 kebab-case，与 manifest 的 name 对应
8. **升级路径**：SKILL.md 头部标注当前 automation 级别；连续 3 次人工零干预跑通可申报 L3（CI 触发）
```

