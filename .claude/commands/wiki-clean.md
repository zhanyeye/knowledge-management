---
description: wiki 治理：lint 检查 + 衰减归档 + 体检，处理重复/冲突/过时
argument-hint: "[--fix]"
allowed-tools: Bash(python .wiki/scripts/wiki.py:*), Read, Edit, Grep, Glob
---

# 治理 wiki

执行并汇报：

```bash
python .wiki/scripts/wiki.py lint $ARGUMENTS   # --fix 顺带重建索引
python .wiki/scripts/wiki.py decay             # 闲置降级 + 零引用 draft 归档
python .wiki/scripts/wiki.py stats             # 体检
```

对每个 WARN/ERROR 给出处置建议并代为执行（需确认的先列出）：

| 问题 | 处置 |
|---|---|
| 手册缺章节/risk | 补齐或降级为流程 |
| 规范冲突（pending/CONFLICTS.md） | 摘录双方规则交维护者仲裁 |
| 疑似重复条目 | 对比合并，保留一条 |
| draft 闲置超期 | 找人 /wiki-verify，或同意后归档 |
| related 悬空 | 修正或删除该字段 |

治理完成后 `python .wiki/scripts/wiki.py index`。
