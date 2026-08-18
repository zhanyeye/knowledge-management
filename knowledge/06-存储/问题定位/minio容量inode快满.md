---
title: MinIO 存储空间/inode 快满
owner: null
kind: playbook
maturity: draft
risk: medium
automation: L0
symptoms: [minio容量, 存储告警, inode满]
tags: [minio, 存储, 容量, 磁盘]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# MinIO 存储空间/inode 快满

## 症状
- 表现：监控告警存储空间或 inode 使用率接近阈值
- 影响面初判：使用 MinIO 的业务写入（TODO：确认业务清单与影响）

## 排查路径

### 1. 查看监控确认水位与增长趋势
- TODO：监控面板入口（registry 待建）

### 2. 梳理桶数据占用
- 逐桶统计对象数量与占用（TODO：mc admin 命令待确认）
- 识别异常大桶 / 异常增速桶

### 3. 确认目录规则并配置生命周期
- 问应用开发确认各桶数据的目录规则与保留要求
- 手工配置/调整桶生命周期规则（过期删除）

## 常见根因

| 根因 | 特征 | 处理 |
|---|---|---|
| 桶无生命周期规则 | 数据只进不出 | 配置过期策略 |
| TODO | | |

## 升级条件
- 增长过快即将写满且无法确认可删数据：找 MinIO owner 决策扩容（TODO：补 owner 与扩容流程）

## 关联
- registry：TODO（minio 实例台账待建）
