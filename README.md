# 团队 Wiki

团队知识放一个 Git 仓库：Markdown + 零依赖引擎，配 Claude Code 使用——**查知识、存经验都由 Agent 完成**；
不用 Agent 也能当普通文档库浏览。

## 快速开始

```bash
git config core.hooksPath .githooks    # ① 启用提交检查（clone 后跑一次）
git config core.quotepath false        #    中文文件名在 git status 正常显示
python .wiki/scripts/wiki.py init      # ② 初始化目录与索引
```

③ 用 Claude Code 打开本仓库，直接问：`/wiki rancher 登录不上怎么回事`

**刚起步的空库建议先导入旧文档**（旧 wiki / ADR / runbook / FAQ / 资产清单）：
在 Claude Code 里执行 `/wiki-import <旧文档目录>`，Agent 会按内容归类、给缺失步骤生成“待专家确认”访谈提纲。

不用 Claude Code：`python .wiki/scripts/wiki.py search "证书"` 检索，或直接浏览 `catalog.md`。

## 日常使用

| 场景 | 命令 |
|---|---|
| 遇到问题想查（排障 / 找规范 / 找手册 / 找历史决策） | `/wiki <一句话描述>` |
| 处理完故障/选型，想把经验留下 | `/wiki-save` |
| （维护者）批量导入旧 wiki | `/wiki-import <目录>` |
| （维护者）定期治理清理 | `/wiki-clean --fix` |

查到的答案标注来源编号与可信度（`draft` 未验证 / `verified` / `proven` 多人多项目验证）；
新存的知识先进 `pending/` 暂存，人工校对后转正。新人 5 分钟走查见 [quickstart](.wiki/docs/quickstart.md)。

## 知识放哪

```
catalog.md        总目录（查知识从这里开始，自动生成）
通用/             跨项目通用的技术知识
基础设施/         数据库/ k8s/ 网络/ 存储/ 发布/ 资产/（各一个子目录）
项目/             各项目知识：一项目一子目录，README 即项目画像
pending/          新知识暂存（人审后转正）      archive/  闲置归档（可恢复）
```

每条知识是六种类型之一：**现状**（是什么）、**决策**（为什么这么选，ADR 即此类）、**规范**（必须/禁止）、**踩坑**（坑与解法）、**流程**（步骤）、**手册**（可执行的运维操作）。
条目示例：[example-entry.md](.wiki/examples/example-entry.md)。框架（引擎/模板/文档/配置）都在隐藏目录 `.wiki/` 里，平时不用进。

## 怎么运转：三个机制

| 机制 | 解决什么 | 一句话原理 |
|---|---|---|
| 三级成熟度 + 自动衰减 | 知识会过时、会腐化 | 可信度 `draft→verified→proven` 由真人验证升级；长期没人用自动降级归档——用进废退 |
| 三级索引 + 查询预算 | Agent 检索炸上下文 | 总目录 → 目录索引 → 按预算读全文（排障≤3条）；命中记引用续命 |
| Lint 治理 | 知识库膨胀 | 提交时自动查格式/手册必备章节/重复/规范冲突/悬空引用，不合格进不了库 |

```
/wiki 查 ─→ 用 ─→ 记引用（续命）     没查到 ─→ 处理 ─→ /wiki-save 存
        └→ pending 人审转正 → /wiki-verify 验证升级 → 持续被用
           长期没人用：自动降级/归档 · 膨胀/冲突：lint 拦截
```

## 自定义与导入

```bash
python .wiki/scripts/wiki.py layer add 基础设施/监控 --prefix MON --title "基础设施·监控"
python .wiki/scripts/wiki.py type add 复盘 --title "故障复盘"
python .wiki/scripts/wiki.py new 复盘 "XX故障复盘" --layer 基础设施/监控    # 立即可用
```

分区和类型随意增减（`layer list` / `type list` 查看全部）。导入旧文档按内容性质归类、不保留原目录形态
（ADR→决策、runbook→手册、FAQ→拆成踩坑/现状、registry→基础设施/资产），完整规则见 `/wiki-import`。

## 更多文档

- 新人上手：[quickstart](.wiki/docs/quickstart.md)
- 配置参考：[configuration](.wiki/docs/configuration.md)
- Agent 协作契约（给 Claude Code / opencode 看的规则）：[CLAUDE.md](CLAUDE.md)
