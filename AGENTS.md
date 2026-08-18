# AGENTS.md — 基础设施知识库协作契约

本仓库是基础设施团队知识库：Markdown/YAML 知识 + `scripts/infra.py` 引擎（纯标准库，零依赖）+ `.claude/skills/` 任务型自动化。
适用于 Claude Code / ZCode / Cursor / 其他 CLI Agent。**本文件是唯一契约**，不要再建 .cursor/.claude 命令副本。

## 一、动手前先查（三级索引 + 查询预算）

任何排障 / 变更 / 定位 / 咨询任务，先按索引检索，禁止 grep 全库：

1. 读 `INDEX.md`（总索引）；若全库为空，直接告知并建议走 infra-import 导入
2. 读目标分区的 `INDEX.md`（一行一条）
3. 按预算读条目全文（预算在 `scripts/infra.json` → `budgets`，按任务类型）

辅助定位：`python scripts/infra.py search <关键词> --limit 3`（标题/标签/H2/正文加权，含草稿箱）。

**命中并使用知识后必须记引用**：`python scripts/infra.py reference <相对路径> --in "<上下文>"`。
引用写 `.infra/refs-YYYY.jsonl` 侧车日志，不改条目；无引用的手册会被 decay 降级归档。

## 二、什么放哪里（七类判定表）

| 问题 | kind | 放哪 | 反例 |
|---|---|---|---|
| 这个东西在哪/谁负责/入口是啥 | registry | `台账/<对象类型>/<名称>.yaml`（集群/数据库/中间件/域名/证书/存储/观测/平台/服务/虚机） | 不要在 md 里堆资产清单 |
| 这件事怎么做/怎么回滚 | runbook | `手册/<域>/<名称>.md`（域：k8s/网络/域名/证书/虚机/发布/数据库/观测/平台） | 按动作组织，不按组件 |
| 这个症状怎么查 | playbook | `排障/<名称>.md`（如 磁盘满/微服务重启分析/Helm部署失败） | 按症状组织，不按组件 |
| 为什么这样设计 | adr | `决策/NNNN-<名称>.md`，编号连续 | — |
| 高频短问答 | faq | `问答/<域>.md` | 长流程放手册 |
| 链路/拓扑/数据流 | architecture | `架构/{拓扑,请求链路,数据流}/` | 必须带 mermaid |
| 真实故障复盘 | case | `案例/<年>/` | 只写有复盘价值的故障 |

命名：**目录与文件名用中文**（产品名/命令保留英文，如 MinIO容量告急.md、node-agent灰度发版.md）；
frontmatter 的 `kind` 用英文标识（registry/runbook/playbook/adr/faq/architecture/case）。文件路径即 ID。

## 三、写入规则（唯一写入口是 草稿箱/）

1. 新知识（无论 AI 导入还是人写）先落 `草稿箱/`：`python scripts/infra.py new <kind> <名称> --title "<中文标题>"`
2. 套 `templates/<kind>` 模板补内容；**禁止编造**：原始材料没有的信息写 `TODO`，不确定的命令参数标 `待确认`
3. 涉及具体资源对象的，同步补/更新对应 `台账/*.yaml` 的 `knowledge.*` 链接（跨文件关联唯一源）
4. 跑 `python scripts/infra.py lint` 必须零错误
5. 人工 review 后转正：`git mv 草稿箱/<文件> <目标分区>/` → `python scripts/infra.py index` → 提交

## 四、运维执行安全（risk 分级）

执行手册/排障条目前完整读全文，按 frontmatter `risk` 分级：

- **low**：只读诊断（kubectl get/describe/logs/top、df、看面板）可直接执行
- **medium**：有变更效果（重启、清理、改配置）——展示步骤清单，逐项人工确认后执行
- **high**：生产高危（证书切换、批量主机操作、数据删除、核心组件发版）——只输出人工执行指引，Agent 不代跑；分步执行、每步验证后收尾

条目未标 risk 的按 high 处理。没有手册的 high 风险操作，先推动沉淀手册再执行。

## 五、治理

- 成熟度：draft（未确认）→ verified（owner/非作者确认，`infra.py verify <路径>`）→ proven（实战检验，`--proven`）
- 衰减：手册/排障 6 个月无引用/复审信号自动降级；draft 归档需 `decay --fix`；台账豁免（靠 last_reviewed 90 天 lint 告警）
- 治理动作：`python scripts/infra.py {index,search,lint,decay}`，lint 错误清零才能提交
- 归档/ 可逆：git mv 回来即可

## 六、任务入口（.claude/skills/，ZCode/Claude Code 自动加载）

| 场景 | skill |
|---|---|
| 「XX 在哪/谁负责/入口」 | infra-locate |
| 「我要做 XX（配域名/换证书/扩容…）」 | infra-change |
| 「XX 出问题了 / XX 症状」 | infra-troubleshoot |
| 「把这批文档/场景整理入库」 | infra-import |
| 引擎直调 | `python scripts/infra.py {index,search,lint,decay,reference,verify,new}` |

## 七、目录

```
INDEX.md   总索引（自动生成）   台账/     资产台账（YAML）
手册/      操作手册（按动作）   排障/     排障手册（按症状）
决策/      决策记录           问答/     高频问答
架构/      拓扑/链路（mermaid） 案例/     故障复盘（按年）
草稿箱/    新知识唯一写入口     归档/     衰减归档（可逆）
templates/ 七套模板           scripts/  infra.py + infra.json + 测试
.infra/    refs-*.jsonl 引用旁车 + 操作日志    .background/ 设计资料（不参与索引）
```
