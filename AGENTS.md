# AGENTS.md — 团队 Wiki 协作契约

本仓库是团队 wiki：Markdown 知识 + `.wiki/scripts/wiki.py` 引擎（纯标准库 Python，无依赖）。
适用于 Cursor / Claude Code / opencode / 其他 CLI Agent。

## 一、动手前先查

任何排障/开发/运维任务，先按索引检索（禁止 grep 全库）：

1. 读 `catalog.md`（总目录）；**若共 0 条，直接告知空库并建议 `/wiki-import`，不要空转索引**
2. 读目标目录的 `catalog.md`（一行一条）
3. 按预算读条目全文（预算见 `.wiki/config.json` → `query_budgets`）

辅助定位：`python .wiki/scripts/wiki.py search <关键词> --limit 3`（检索含正文）

命中知识后记引用：`python .wiki/scripts/wiki.py reference <编号> --in "<上下文>"`。
引用写入 `.wiki/logs/refs-YYYY.jsonl`，**不改条目 frontmatter**；不记引用会被 decay 降级归档。

## 二、结束后要沉淀

`/wiki-save` 提取候选 → `pending/` 暂存 → 人工确认 → `python .wiki/scripts/wiki.py promote --file pending/<文件> --to <分区>` 转正。
正文套 `.wiki/templates/<类型>.md`。禁止：直接写正式分区、编造命令参数、入库任何凭据。

## 三、运维操作安全

执行手册类条目前完整读全文，按 `ops-runbook-guard` skill 分级：
`risk: low` 可自动；`medium` 展示清单确认后执行；`high` **必须人工逐项确认、分步执行、验证后收尾**。
没有手册的 high 风险操作，先推动沉淀手册再执行。

## 四、命令

| 动作 | 命令 |
|---|---|
| 查知识 | `/wiki <问题>` |
| 沉淀经验 | `/wiki-save` |
| 导入旧文档 | `/wiki-import <目录>` |
| 验证升级 | `/wiki-verify <编号> --by <人> --project <项目>` |
| 治理 | `/wiki-clean --fix` |
| 引擎直调 | `python .wiki/scripts/wiki.py {init,index,search,new,verify,reference,promote,decay,lint,stats,doctor,layer,type}` |

## 五、目录

```
catalog.md          总目录（自动生成，勿手改）
通用/               跨项目通用技术
基础设施/           数据库 / k8s / 网络 / 存储 / 发布 / 资产
项目/               各项目（一项目一子目录，README=项目画像）
pending/            新知识暂存（人审后 promote 转正）
archive/            衰减归档（可逆）
.wiki/logs/         操作日志 log-YYYY.md + 引用旁路 refs-YYYY.jsonl

.wiki/              框架（引擎/模板/配置）
```

六种类型：现状 / 决策 / 规范 / 踩坑 / 流程 / 手册（`type add` 可扩展）。

配置参考：[.wiki/docs/configuration.md](.wiki/docs/configuration.md)
