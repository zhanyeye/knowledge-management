# 磁盘占用判读标准（只读诊断的"大脑"）

| 模式 | 特征 | 确认命令（readonly） | 处置方向 |
|---|---|---|---|
| A 日志堆积 | /var/log、应用 logs 目录占比大，文件按天滚动未清理 | `ls -lh <dir>; du -sh <dir>` | 配置轮转/压缩归档；清理走手册 |
| B docker 膨胀 | /var/lib/docker 大 | `docker system df` | prune 建议（change，人工确认） |
| C 构建残留 | 执行机 /tmp、工作目录脏数据 | `du --max-depth=1 /tmp` | 链 `knowledge/03-构建资源管理/问题定位/执行机残留构建失败.md` |
| D 海量小文件 inode 满 | df -i 满而 df -h 不满 | `df -i; find <dir> -type f \| wc -l` | 定位小文件目录（minio 对象/队列） |
| E 幽灵占用 | df 满但 du 总和对不上 | `lsof +L1` 或 `lsof \| grep deleted` | 重启持有进程（change，人工） |
| F 保留块 | ext4 默认保留 5%，非 root 可写满 | `tune2fs -l <dev> \| grep -i reserved` | 评估调低保留比例（change） |

判读原则：
- 命中 A–D 给出 dry-run 建议；E/F 先报告证据链再谈处置
- 任何生产数据删除一律人工
- owner 未知的目录先查 `knowledge/<域>/inventory.yaml`
