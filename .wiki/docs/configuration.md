# 配置参考（.wiki/config.json）

## 自定义分区与类型：优先用命令（自动校验 + 建目录 + 生成模板 + 刷索引）

```bash
python .wiki/scripts/wiki.py layer list                          # 查看全部分区
python .wiki/scripts/wiki.py layer add 基础设施/监控 \
       --prefix MON --title "基础设施·监控"                 # 新增分区
python .wiki/scripts/wiki.py layer rm 基础设施/监控               # 移除（仅允许空分区）
python .wiki/scripts/wiki.py type list                           # 查看全部类型
python .wiki/scripts/wiki.py type add 复盘 --title "故障复盘"     # 新增类型（自动生成模板）
python .wiki/scripts/wiki.py type rm 复盘                        # 移除（仅允许未被使用的类型）
```

- 想分几层、几个域随意：路径即层级（`基础设施/监控` 是 `基础设施` 的子分区，条目归属"最具体的分区"）
- `项目/` 天然递归，新项目直接建 `项目/<项目名>/` 子目录即可，**不用**注册
- 删除有保护：分区下有条目 / 类型被使用时会拒绝，先迁移再删

命令做不了的事（改阈值、预算、衰减月数等）再手工编辑 config.json，改完跑 `python .wiki/scripts/wiki.py init && python .wiki/scripts/wiki.py index`。字段含义如下。

---

## layers —— 分区

```json
"基础设施/k8s": {
  "path": "基础设施/k8s",   // 仓库内相对路径（正斜杠），支持中文
  "prefix": "K8",            // 该分区条目编号前缀（编号 = 前缀-序号，如 K8-001）
  "title": "基础设施·K8s/容器" // 展示名（进入总目录 catalog.md）
}
```

- **加子域**：`layer add 基础设施/监控 --prefix MON --title "基础设施·监控"`（一条命令完成建目录/写配置/刷索引）
- **加项目**：不用改配置——`项目` 分区递归扫描，直接建 `项目/<项目名>/` 子目录放条目即可（编号统一 PRJ-xxx）
- 想让某项目有独立编号前缀，再把它注册进 layers 也行

## types —— 知识类型（默认六种，可增删）

| key | 语义 | 特殊约束（lint） |
|---|---|---|
| 现状 | 事实/拓扑/资产 | — |
| 决策 | 选型/架构决策（ADR） | 建议带备选对比与证据 |
| 规范 | 要求或禁止 | 必填 polarity(recommend/avoid)+理由 |
| 踩坑 | 坑与解法 | 建议带证据 |
| 流程 | 人工流程 | — |
| 手册 | Agent 可执行运维手册 | 必填 risk + 前置检查/验证/回滚章节 |

新增类型：`type add 复盘 --title "故障复盘"`（模板自动生成在 `.wiki/templates/复盘.md`）。
key 支持中文或英文（字母开头）。

## maturity —— 可信度与衰减

```json
"promote": {
  "draft_to_verified":  {"validations": 1},
  "verified_to_proven": {"distinct_validators": 2, "distinct_projects": 2}
},
"decay": {
  "proven_months": 12, "verified_months": 6, "archive_draft_months": 6,
  "evergreen_exempt": true
}
```

- 计时基准：last_referenced → last_verified → created（依次回退）
- 归档 = 移入 `archive/<年>/`，退出索引，可 promote 复活
- **evergreen 豁免**：条目 frontmatter 加 `evergreen: true`（如核心红线、基础操作），decay 全程跳过不降级不归档

## query_budgets —— 查询预算

```json
"troubleshoot": {"layerB_dirs": 2, "full_entries": 3, "hint": "排障：优先 踩坑→手册"}
```

hint 会写进总目录给 Agent 看；任务类型 key 可自由增加。

## lint —— 治理规则

| 键 | 作用 |
|---|---|
| runbook_requires | runbook 正文必须包含的章节名 |
| guideline_polarity_values | polarity 合法值 |
| duplicate_title_jaccard | 标题相似度阈值（重复检测） |

补充规则：`related` 指向不存在的编号 = **ERROR**（挡提交，保证知识图谱不断链）；
规范类冲突检测是**全库按 tag 聚类**（跨分区也能查出相反规范，记录到 `pending/CONFLICTS.md`）。

## frontmatter 字段速查

```yaml
id: K8-001               # 自动生成：分区前缀-序号
title / type / maturity  # 基础三件套（maturity 由验证驱动，不手改）
owner / created          # 责任人与创建日期
last_verified / last_referenced / reference_count / validations   # 引擎维护，勿手改
tags: [a, b]             # 检索词（中英文均可）
related: [其他编号]       # 关联条目（lint 校验存在性）
risk: low|medium|high    # 仅手册类
polarity: recommend|avoid # 仅规范类
evergreen: true           # 可选：豁免衰减（核心红线/基础操作类）
source: wiki导入:<文件>   # 来源溯源
```
