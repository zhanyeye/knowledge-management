---
description: 记录一次人工验证，推动条目可信度升级（draft→verified→proven）
argument-hint: "<编号> --by <验证人> [--project <项目>]"
allowed-tools: Bash(python .wiki/scripts/wiki.py:*)
---

# 验证知识

执行：

```bash
python .wiki/scripts/wiki.py verify $ARGUMENTS
```

然后读该条目，汇报验证记录与可信度变化。规则：draft→verified 需 1 人验证；verified→proven 需 ≥2 人 × ≥2 项目（加 `--promote`）。

用户口头说"XX 条验证过了"时，解析出编号与验证人再执行，缺验证人就问。
