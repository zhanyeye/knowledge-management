---
description: wiki 治理：lint 检查 + 衰减归档 + 体检
---

# 治理 wiki

```bash
python .wiki/scripts/wiki.py lint $ARGUMENTS
python .wiki/scripts/wiki.py decay
python .wiki/scripts/wiki.py stats
python .wiki/scripts/wiki.py index
```

对每个 WARN/ERROR 给出处置建议。引用统计来自 `.wiki/logs/refs-*.jsonl` 与历史 frontmatter 缓存。
