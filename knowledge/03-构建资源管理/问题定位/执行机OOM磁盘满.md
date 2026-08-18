---
title: px 执行机 OOM/磁盘满定位
owner: null
kind: playbook
maturity: draft
risk: medium
automation: L0
symptoms: [执行机oom, 执行机磁盘满, 构建失败]
tags: [px, 执行机, oom, 磁盘, ci]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# px 执行机 OOM/磁盘满定位

## 症状
- 表现：CI 任务在执行机上因 OOM 或磁盘满失败
- 影响面初判：该执行机上的 CI 任务

## 排查路径

### 1. 查看任务日志
- 找到失败任务的日志，确认失败原因（被杀/写失败）（TODO：px 任务日志入口）

### 2. 登录执行节点
```bash
dmesg -T | grep -i oom     # 是否 OOM Kill
df -h                       # 磁盘使用率
```

### 3. 处置
- 磁盘满 → 参照 `px公共文件服务器满` 的 du 下钻清理（TODO：转正后补 related）
- OOM → 看任务内存消耗，考虑换更大规格执行机或优化任务

## 常见根因

| 根因 | 特征 | 处理 |
|---|---|---|
| 执行机脏数据堆积 | 系统盘/工作目录满 | 清理 |
| 任务内存超限 | dmesg OOM 记录 | 调整任务/换机 |
| TODO | | |

## 升级条件
- 多台执行机同时异常：怀疑共性问题，找 px 平台 owner

## 关联
- playbooks：px公共文件服务器满
