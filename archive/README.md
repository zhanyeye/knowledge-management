# archive —— 归档区

`python .wiki/scripts/wiki.py decay` 把"draft 且闲置超期、零引用零验证"的条目移入本区（按年份分目录）。

- 归档 ≠ 删除：内容保留，只是退出索引，不再被检索到；
- 复活：`python .wiki/scripts/wiki.py promote --file archive/<年>/<文件> --to <分区>`（成熟度重置为 draft 重新验证）。
