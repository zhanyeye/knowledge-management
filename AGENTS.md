# AGENTS.md — 基础设施知识库协作契约（方案D域制）

本仓库 = 知识库（`knowledge/` 按域组织）+ 自动化脚本（`scripts/` + manifest 注册表）+ 技能层（`.claude/skills/`）。
引擎 `scripts/infra.py`（纯标准库，零依赖）。适用于 Claude Code / ZCode / Cursor / 其他 CLI Agent。
**本文件是唯一契约**，不要再建 .cursor/.claude 命令副本。

## 一、路由中枢（遇到问题先走这里）

```
排障（"XX 出问题了/XX 症状"）：
  读 问题定位索引.md（症状→域→文档→脚本→skill）→ 有原子 skill 用 skill
  → 无则读域内 问题定位/ 文档 → 仍无则 search/INDEX 逐级查 → 事后沉淀

定位（"XX 在哪/谁负责/入口"）：
  查 域路由表.yaml 定位域 → 读 knowledge/<域>/inventory.yaml

变更（"我要做 XX"）：
  search --kind runbook / 域 INDEX → 完整读手册 → 按「三层闸门」执行

入库（"把这份笔记/文档整理进库"）：
  infra-import 流程（见 skill）：分类 → new 生成 → 填内容（禁编造，缺项 TODO）→ lint
```

索引三级：`INDEX.md`（总）→ `knowledge/<NN-域>/INDEX.md`（域）→ 条目全文。
预算按任务类型在 `scripts/infra.json` → `budgets`。
辅助：`python scripts/infra.py search <关键词> --limit 3`（标题/标签/H2/正文加权）。

## 二、什么放哪里（11 域 × 8 类）

域：`00-通用环境基线 01-镜像制作 02-k8s资源管理 03-构建资源管理 04-网络管理 05-数据库 06-存储 07-消息中间件 08-数据工程与AI平台 09-业务平台对接 10-研发效能与协同`（键名见 域路由表.yaml，agent 寻址不靠记编号）

| kind | 放哪 | 说明 |
|---|---|---|
| registry | `knowledge/<域>/inventory.yaml` | 每域一份多资源台账（在哪/谁负责/入口/依赖） |
| runbook | `knowledge/<域>/**`（含子目录） | 操作手册：怎么做/怎么回滚，带前置/验证/回滚 |
| playbook | `knowledge/<域>/问题定位/` | 排障手册：按症状组织，标 `symptoms` 进症状索引 |
| case | `knowledge/<域>/复盘/` | 故障/改进复盘 |
| adr | `knowledge/<域>/方案设计/` | 决策/RFC——**明确非可执行**，agent 不得当步骤执行 |
| reference | `knowledge/<域>/` 顶层 | 基线/约定：只写内部与通用标准的不同处 |
| faq / architecture | `knowledge/<域>/faq*.md` / `architecture*.md` | 问答 / 链路图（必带 mermaid） |

命名：目录英文+序号，文件名中文（产品名保留英文）。路径即 ID。

## 三、写入规则（直接写目标位置，git 即评审）

1. `python scripts/infra.py new <kind> <名> --domain <域键>` 生成骨架（maturity=draft）
2. 套模板补内容；**禁止编造**：原始材料没有的信息写 `TODO`，不确定命令标 `待确认`
3. playbook 标 `symptoms`（进问题定位索引）；配了脚本标 `script`（必须已登记 manifest）
4. 涉及资源对象 → 同步 `inventory.yaml` 的 `knowledge.*` 链接（跨文件关联唯一源）
5. `python scripts/infra.py lint` 零错误 → commit（git diff/PR 即人审）→ `index` 刷新索引

## 四、执行安全（三层闸门）

agent 执行任何动作前依次过：

1. **脚本在 `scripts/manifest.yaml` 里吗？** 不在 → 不允许凭空跑
2. **manifest 的 risk_level？** `readonly` → 可直接执行（只读诊断）
3. **`change` → 查 related_doc 手册的 risk**：medium 逐项确认后执行；high 只输出人工指引

手册未标 risk 按 high 处理；没有手册的 high 风险操作，先沉淀手册再执行。
原子 skill 编写规范见 `设计方案/方案D-合并版-知识Skill化与自动化.md` 第十节（单一职责/只读优先/change 必带 dry-run/登记才可执行/知识不搬家/留痕闭环）。

## 五、自动化四级（知识 skill 化的推进仪表盘）

`L0 文档 → L1 脚本化(manifest 登记) → L2 skill 化(SKILL.md+脚本+判读) → L3 自动化(CI 触发)`
frontmatter 标 `automation`，INDEX.md 展示各域分布。不强求全 L3，高频/高危优先。
连续 3 次零人工干预跑通可申报 L3。执行留痕：结论写 `reports/YYYY-MM-<主题>.md`。

## 六、治理

- 成熟度：draft → verified（`infra.py verify <路径>`）→ proven（`--proven`，实战检验）
- 衰减：手册/排障 6 个月无引用/复审信号自动降级；draft 闲置由 decay 报「建议删除」（人工 git rm，历史可恢复）；台账走 last_reviewed 90 天告警
- **命中并使用知识必须记引用**：`python scripts/infra.py reference <路径> --in "<上下文>"`
- CI（.github/workflows/lint.yml）：lint + 单测，错误清零才能合入

## 七、命令与目录

```
python scripts/infra.py {index,search,lint,decay,reference,verify,new}

任务入口（.claude/skills/）：infra-locate / infra-change / infra-troubleshoot / infra-import
斜杠命令（.claude/commands/，薄路由）：/infra 查询 · /infra-import 导入 · /infra-exec 执行
原子技能（.claude/skills/<域>/<名>/）：如 storage/disk-usage-diagnose

INDEX.md 总索引          问题定位索引.md 症状路由     域路由表.yaml agent寻址
knowledge/ 知识库（11域） scripts/ 引擎+脚本+manifest  templates/ 模板
reports/ 执行留痕        .infra/ 引用旁车+日志        .background/ .设计方案/ 设计资料
```
