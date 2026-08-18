---
title: px 执行资源排队堆积
owner: null
kind: playbook
maturity: draft
risk: medium
automation: L1
symptoms: [排队, 任务等待, 执行资源不足]
script: scripts/build/px_queue_check.sh
tags: [px, ci, 排队, 资源]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# px 执行资源排队堆积

## 症状
- 表现：CI 任务长时间排队等不到执行资源
- 影响面初判：全团队发布/构建效率

## 排查路径

### 1. 查看队列状态
- 找到任务堆积的集群/队列（TODO：队列状态查看入口）

### 2. 找可让路的大批量任务
- 找大批量启动的流水线，评估能否暂停让路（需与属主确认）

### 3. 处理镜像拉取阻塞
- 镜像拉取不到导致容器阻塞的任务：
  ```bash
  kubectl get jobs -n <ns>          # 找 Pending/Blocked 的 job
  kubectl delete job <name> -n <ns> # 手动清理（删除前确认任务可重跑）
  ```

## 常见根因

| 根因 | 特征 | 处理 |
|---|---|---|
| 执行机总量不足 | 队列常态堆积 | 走扩容 runbook（executor-scale） |
| 镜像拉取失败 | job 卡 ImagePull | 清理 job，修镜像源 |
| TODO | | |

## 升级条件
- 需要暂停他人流水线或扩容：找属主/平台 owner 确认

## 关联
- runbooks：TODO executor-scale
