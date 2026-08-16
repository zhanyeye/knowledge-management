# pending —— 新知识暂存区

Agent 或个人提取的知识候选**先进这里**，经人确认后再转正，防止"AI 顺手写一条没人校对的知识"污染 wiki。

## 流程

1. `/wiki-save`（或手工）把候选写为 `pending/<日期-主题>.md`（id 可填 TBD）
2. 人工校对事实、步骤、risk 等级
3. 转正：
   ```bash
   python .wiki/scripts/wiki.py promote --file pending/<文件>.md --to <目标分区>
   ```
   自动重新编号、成熟度重置为 draft、写日志并刷新索引。

## 放哪个分区

| 内容 | 分区 |
|---|---|
| 跨项目通用技术 | `通用` |
| 基础设施（数据库/k8s/网络/存储/发布/资产） | `基础设施/<子域>` |
| 某个项目的知识 | `项目/<项目名>`（新项目先建子目录） |
| 只对一个项目有用但不想进团队库 | 留在项目仓 `docs/wiki/`（见 .wiki/templates/layer3-project/） |

与现有知识冲突的：讨论结论记在 `pending/CONFLICTS.md`（lint 自动追加疑似冲突），再合入。
