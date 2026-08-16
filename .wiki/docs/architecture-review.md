# 知识库架构评估与优化方案

> 本文档是对团队 Wiki 三层架构（分区 × 六类型 × 三级成熟度 × 自动衰减）的深度评估与改进路线图。

> **术语对照（2026-08 中文化后）**：model→现状、decision→决策、guideline→规范、pitfall→踩坑、process→流程、runbook→手册；分区 tech→通用、infra→基础设施、projects→项目。本文按旧英文术语撰写，实施时请按此对照。

**评估日期**：2026-08-16  
**当前版本**：v2（`.wiki/config.json` version 2）  
**核心引擎**：`.wiki/scripts/wiki.py`（700 行，纯 Python 标准库）

---

## 一、架构概览

### 核心设计

```
存储形态：每条知识 = 一个 Markdown 文件
         ├─ frontmatter：元数据（id/type/maturity/owner/created/...）
         └─ body：正文内容（套用 .wiki/templates/<类型>.md）

分区（layers）：tech/（通用）| infra/{database,k8s,network,storage,cicd}/ | projects/（一项目一子目录）
六类型：model 现状 | decision 决策 | guideline 规范 | pitfall 踩坑 | process 流程 | runbook 手册
三级成熟度：draft → verified → proven（由验证证据驱动，不可手改）

消费闭环：catalog.md（总入口）→ 目录索引 → 预算受控检索 → reference 记录引用 → 防衰减
治理机制：git pre-commit lint（ERROR 挡提交）+ 冲突自动记录到 pending/CONFLICTS.md + 衰减归档
```

### 当前规模

| 指标 | 值 | 备注 |
|---|---|---|
| 代码量 | 700 行 | `.wiki/scripts/wiki.py` 纯标准库 |
| 配置中心 | 1 个文件 | `.wiki/config.json` |
| 模板 | 6 种 | `.wiki/templates/<类型>.md` |
| 分区 | 8 个 | tech + infra/5 子域 + projects |

---

## 二、锐评：三维评估

### 2.1 可维护性（7/10）—— 好在零依赖，隐患在自动化

#### ✅ 做得好的地方

1. **零依赖是明智之选**
   - 700 行纯 Python 标准库，5 年后还能跑
   - 自写 frontmatter 解析器换来可移植性，在这个规模上是划算的
   - 没有要求安装 pip/ npm / docker，降低了部署门槛

2. **配置集中化**
   - 分区/类型/阈值/预算全在 `.wiki/config.json`
   - 调参不需要动代码
   - `registered_layers()` 按路径长度排序自动匹配最具体的分区，新项目零接入成本

3. **文件格式极简**
   - 每个条目独立 Markdown，git 友善
   - 元数据全在 frontmatter，人可读 + 机可解析
   - `git diff` 一目了然

#### ⚠️ 隐患

1. **衰减机制靠手动跑**（**高危**）
   - 目前没有自动触发 decay 的钩子
   - 如果忘记跑，"用进废退"就失效了，知识库会膨胀
   - **影响**：核心治理机制失效

2. **预算约束是软约束**（**中危**）
   - Agent 理论上可以绕过 `/wiki` 直接 `Grep/Glob`
   - 要硬限制得在 git hook 里，但成本太高
   - **影响**：检索可能退化成 grep 全库

3. **lint 冲突检测范围有限**（**低危**）
   - 相反 polarity 的 guideline 只在**同目录**检测
   - 如果两个冲突规范分居 `infra/k8s/` 和 `infra/network/`，查不出来
   - **影响**：跨域规范冲突会遗漏

---

### 2.2 上手难易程度（6/10）—— 门槛中偏高，之后流畅

#### 新人的体验曲线

| 阶段 | 体验 | 坎在哪里 |
|---|---|---|
| 第 0 天：**读 wiki** | 顺畅 ✅ | `catalog.md` 入口清晰 |
| 第 7 天：**第一次写 pending** | 要记模板 ⚠️ | 六种类型各有强制字段，得看模板 |
| 第 30 天：**第一次做 verify** | 要理解成熟度机制 ⚠️ | 为什么要两人两项目才能晋升 proven？ |
| 第 90 天：**第一次遇到 decay** | 有点懵 ⚠️ | "我写的怎么被降级了？" |

#### 关键摩擦点

1. **`/wiki` 强制记 reference**
   - 这是"用进废退"的命脉，但对新人来说是额外动作
   - 他们第一次排障时只想找答案，不想理解"为什么要记引用"
   - **需要**：Team Leader 站队强调

2. **runbook 的 risk + 三章节**
   - 强制要求是对的，但第一次写的人会忘
   - 好在 lint ERROR 会挡提交，能形成肌肉记忆

3. **`related` 悬空只有 WARN**
   - 建议降级为 ERROR，不然没人修，知识图谱永远是碎的

#### 流畅之后

一旦形成"查→用→记引用→沉淀"的闭环，系统会自运转。关键是前 30 天的 Onboarding 要有人盯着执行。

---

### 2.3 可扩展性（8/10）—— 横向够用，纵向有瓶颈

#### 横向（知识量/项目数）

| 指标 | 当前设计能撑到 | 需要演进 |
|---|---|---|
| 条目总数 | ~500 条 | 检索是 O(n) 词元匹配，500 条内够用 |
| 项目数 | 无限制（一项目一子目录） | 只要分区注册表不乱，任意多 |
| 并发写入 | Git 冲突解决（非同时使用） | 每人本地一份，不存在并发问题 |

#### 纵向（复杂度增长）

1. **检索是词元不是语义**
   - 同义词查不到时，目前靠 tags 弥补
   - 到 500+ 条时，建议升级到向量索引（可配：词元做第一道，向量做 fallback）

2. **预算是静态配置**
   - 目前按任务类型定死
   - 实践中"排障一个 K8s 问题"和"排障一个网络问题"需要的信息量不同
   - 未来可以按**分区**定制预算

3. **成熟度阈值是硬编码**
   - draft→verified 要 1 人验证，写死在 config 里
   - 如果要细分（某些类型要求 2 人），得扩展 schema

4. **衰减策略一刀切**
   - proven 12 月降 verified，但有些知识即便没人用，也不该降级
   - 建议加个 `evergreen: true` 标记豁免衰减

---

## 三、优化方案（按优先级）

### P0：立即修复（本周）

#### 3.1 把 decay 挂进例行流程

**问题**：衰减机制靠手动跑，容易忘记，导致"用进废退"失效。

**方案 A**：修改 `/wiki-clean` 命令，默认执行 decay
```bash
# 在 knowledge-curator agent 的执行逻辑里，每次跑 lint 后自动跑 decay
python .wiki/scripts/wiki.py lint && python .wiki/scripts/wiki.py decay
```

**方案 B**：加 CI 定时任务（推荐）
```yaml
# .github/workflows/wiki-maintenance.yml
on:
  schedule:
    - cron: "0 0 1 * *"  # 每月 1 号凌晨
  workflow_dispatch:  # 也支持手动触发
jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python .wiki/scripts/wiki.py decay
      - run: python .wiki/scripts/wiki.py index
      - run: git config user.name && git commit -am "auto: wiki decay" && git push
```

**验收**：跑一次 decay，观察 `log.md` 是否有记录；一个月后看 stats 是否有降级/归档。

---

#### 3.2 `related` 悬空升为 ERROR

**问题**：目前是 WARN，没人修，知识图谱永远是碎的。

**方案**：修改 `.wiki/scripts/wiki.py` lint 部分
```python
# 第 469-471 行左右
for rid in m.get("related") or []:
    if rid not in all_ids:
        issues.append(f"{e.id}: related 指向不存在的 {rid}")  # 从 warnings 改为 issues
```

**验收**：故意写个 `related: ["K8-999"]`，跑 lint 应该挡提交。

---

### P1：短期优化（本月）

#### 3.3 扩展 lint 冲突检测范围

**问题**：相反 polarity 的 guideline 只在同目录检测，跨域冲突查不出。

**方案**：修改 `.wiki/scripts/wiki.py` lint 部分，改为全库检测
```python
# 第 496-509 行左右
# 把 by_dir 改为 by_tags，按标签聚类检测
by_tags = {}
for e in entries:
    if e.type == "guideline":
        for tag in e.meta.get("tags") or []:
            by_tags.setdefault(tag, []).append(e)
conflicts = []
for tag, es in by_tags.items():
    for i in range(len(es)):
        for j in range(i + 1, len(es)):
            a, b = es[i], es[j]
            # 原有逻辑不变，但不再限制同目录
            if a.meta.get("polarity") and b.meta.get("polarity") \
                    and a.meta["polarity"] != b.meta["polarity"] \
                    and _title_jaccard(a.title, b.title) >= 0.3:
                conflicts.append(f"{a.id}({a.meta['polarity']}) vs {b.id}({b.meta['polarity']}) — {a.title}（标签: #{tag}）")
```

**验收**：在 `infra/k8s/` 和 `infra/network/` 各写一个相反 polarity 的 guideline（同标签），跑 lint 应该检测出。

---

#### 3.4 加 `evergreen` 标记豁免衰减

**问题**：有些核心知识（如"如何重启 K8s 集群"）即便没人用，也不该降级。

**方案**：
1. 在 `.wiki/config.json` 加配置
```json
"decay": {
  "proven_months": 12,
  "verified_months": 6,
  "archive_draft_months": 6,
  "evergreen_exempt": true  // 新增：evergreen=true 的条目豁免衰减
}
```

2. 修改 `.wiki/scripts/wiki.py` decay 部分
```python
# 第 414-419 行左右
if e.maturity == "proven" and months >= dcfg["proven_months"]:
    if not e.meta.get("evergreen"):  // 新增判断
        e.meta["maturity"] = "verified"
        actions.append(f"{e.id} proven→verified (闲置 {months} 月)")
```

**验收**：给某条 proven 加 `evergreen: true`，跑 decay 应该不降级。

---

### P2：中期演进（下季度）

#### 3.5 向量索引作为 fallback

**问题**：检索是词元匹配，同义词查不到。

**方案**：
1. 加一个可选的向量索引插件（用 sentence-transformers）
2. 检索时先跑词元匹配，结果不足 3 条时再跑向量匹配
3. 用 `config.json` 控制开关

```python
// 伪代码
def search(query, cfg):
    results = keyword_search(query)
    if len(results) < 3 and cfg.get("vector_search_enabled"):
        results.extend(vector_search(query))
    return results[:budget]
```

**验收**：搜"容器编排"应该能查到写的是"K8s"的条目。

---

#### 3.6 按分区定制查询预算

**问题**：目前预算按任务类型定死，但实践中不同分区的信息密度不同。

**方案**：在 `.wiki/config.json` 支持分区级覆盖
```json
"query_budgets": {
  "default": {"layerB_dirs": 2, "full_entries": 5},
  "troubleshoot": {"layerB_dirs": 2, "full_entries": 3}
},
"layer_overrides": {
  "infra/k8s": {"query_budgets": {"troubleshoot": {"full_entries": 5}}},  // K8s 排障可能要看更多
  "infra/network": {"query_budgets": {"troubleshoot": {"full_entries": 4}}}
}
```

**验收**：搜 K8s 问题时，应该能读到 5 条全文而不是 3 条。

---

## 四、验收清单

优化完成后，用这个清单验收：

| 项 | 验收方式 | 状态 |
|---|---|---|
| decay 自动化 | 跑一次 CI 或 `/wiki-clean`，看 log.md 有记录 | ⬜ |
| related 悬空 ERROR | 故意写 `related: ["K8-999"]`，lint 挡提交 | ⬜ |
| 冲突检测全库 | 跨域写相反 polarity 的 guideline，lint 检测出 | ⬜ |
| evergreen 豁免 | 给 proven 加 `evergreen: true`，decay 不降级 | ⬜ |
| 向量索引 fallback | 搜同义词，能查到 | ⬜（中期） |
| 分区预算覆盖 | 搜 K8s 问题，读到 5 条全文 | ⬜（中期） |

---

## 五、总体评价

| 维度 | 评分 | 关键词 | 最该补的两件事 |
|---|---|---|---|
| 可维护性 | 7/10 | 零依赖、git 友善，但 decay 要自动化 | 1. decay 挂进 CI 或 `/wiki-clean`<br>2. related 升 ERROR |
| 上手难度 | 6/10 | 前 30 天需牵引，之后流畅 | 1. 写 Onboarding 文档<br>2. Team Leader 站队强调 |
| 可扩展性 | 8/10 | 横向无上限，纵向到 500 条需演进 | 1. 预留向量索引接口<br>2. 预留分区预算覆盖 |

**核心优点：**
- "用进废退"闭环设计到位（reference → 衰减 → 归档）
- 治理机制务实（lint 挡提交、verify 门槛不高但有效）
- 技术选型克制（700 行纯 Python，零依赖）

**核心风险：**
- 衰减机制若不自动化，膨胀会卷土重来
- 预算约束若被绕过，检索会退化成 grep 全库
- lint 冲突检测范围有限，跨域规范冲突会遗漏
