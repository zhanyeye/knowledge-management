---
name: disk-usage-diagnose
description: 磁盘/inode 告警或写满时的只读诊断。输入目标主机，输出占用画像、疑似根因与处理建议（不执行清理）。当用户说「磁盘满了 / inode 满了 / no space left / 写文件失败」或收到存储容量告警时使用。
---

# 磁盘占用诊断（只读）

## 何时使用
- 监控告警磁盘或 inode 使用率超阈值
- 应用报 No space left on device / 写文件失败
- 执行机 / 公共文件服务器 / MinIO 宿主机疑似写满

## 前置确认（动手前必查）
1. 目标主机与疑似路径；不知道路径先查 `knowledge/06-存储/inventory.yaml`
   （或 `knowledge/03-构建资源管理/inventory.yaml` 执行机池），用 infra-locate 定位
2. 只需要只读登录权限
3. 本技能只诊断不清理：任何清理/删除动作转 infra-change 走对应手册（risk 分级）

## 步骤
1. 整体画像（标出超 85% 的挂载点，含 inode）：
   ```bash
   bash scripts/storage/disk_usage_scan.sh <host> --quick
   ```
2. 对每个超阈值挂载点下钻两层，取 TOP 占用：
   ```bash
   bash scripts/storage/disk_usage_scan.sh <host> --path <挂载点> --depth 2
   ```
3. 按 [references/judgment.md](references/judgment.md) 的模式表判读：
   - 命中「已知可清理模式」→ 给出建议命令（一律带 --dry-run），交人工或 infra-change 确认执行
   - 未命中/未知大目录 → 报告路径+大小+属主线索，查 inventory 定位资源 owner
4. 收尾两件事：
   - 结论写 `reports/YYYY-MM-磁盘诊断-<host>.md`
   - `python scripts/infra.py reference knowledge/06-存储/问题定位/px公共文件服务器满.md --in "<简述>"`

## 输出格式
- `<host>` 磁盘画像（df -h / df -i，超阈值项加标）
- TOP 占用目录（大小 + 最后修改时间线索）
- 疑似根因（按 judgment.md 模式编号）+ 置信度
- 建议动作清单（readonly=已执行；change=待人工确认，逐条附命令）

## 升级条件
- df 满但 du 找不到大文件 → 已删除文件被进程持有（judgment.md 模式 E），需重启持有进程
- 涉及生产数据删除 → 一律人工，本技能止步于建议
- MinIO 对象存储容量问题 → 转其容量 playbook（生命周期策略路径不同）
