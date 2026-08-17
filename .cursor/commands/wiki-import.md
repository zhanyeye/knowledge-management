---
description: 批量导入旧 wiki/文档为条目（冷启动）
---

# 导入旧文档

来源：$ARGUMENTS（多文档分批，每批 ≤10 份）

按内容性质归类：ADR→决策、runbook→手册、FAQ→踩坑/现状/流程、registry→基础设施/资产。

每份：读入脱敏 → 归类 → `python .wiki/scripts/wiki.py new <类型> "<标题>" --layer <分区> --source "wiki导入:<文件>"` → `python .wiki/scripts/wiki.py index`。

导入条目一律 draft。完整规则见 `.claude/commands/wiki-import.md`。
