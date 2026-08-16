---
description: 批量导入旧 wiki/文档为条目（冷启动）
argument-hint: "[旧文档目录/文件列表]"
allowed-tools: Bash(python .wiki/scripts/wiki.py:*), Read, Write, Grep, Glob
---

# 导入旧文档

来源：$ARGUMENTS（多文档分批，每批 ≤10 份）

按**内容性质**归类，不保留原目录形态：

| 旧形态 | 去处 |
|---|---|
| ADR 决策记录 | type=决策 |
| runbook 运维手册 | type=手册（必须补 risk 与 前置检查/验证/回滚） |
| FAQ | 按条拆：问题+解法→踩坑；事实问答→现状；办事步骤→流程 |
| registry/资产清单 | --layer 基础设施/资产，type=现状 |
| 混合 docs | 按内容拆成多条逐条归类 |

每份四步：

1. **读入并脱敏**（内网地址→`<内网地址>`，凭据→删除）。
2. **归类**：type（现状/决策/规范/踩坑/流程/手册）+ 目标分区（通用 / 基础设施/<子域> / 项目/<项目>）。判断不了放 `通用` 并在报告标记"待归类"。
3. **生成**：
   ```bash
   python .wiki/scripts/wiki.py new <类型> "<原题目>" --layer <分区> --owner <维护者> --source "wiki导入:<原文件名>"
   ```
   正文按模板整理：有价值的内容保留；过时的删掉并注明"导入待核"；手册缺失的章节写成"待专家确认"清单——这份清单就是后续专家访谈提纲。
4. **收尾**：`python .wiki/scripts/wiki.py index`，输出报告：条目清单（编号/类型/分区/完成度）、待专家确认项汇总。

导入条目一律 draft，由 /wiki-verify 逐步晋升。
