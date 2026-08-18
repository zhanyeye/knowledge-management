---
title: node-agent 灰度发版
owner: null
kind: runbook
maturity: draft
risk: high
automation: L0
tags: [node-agent, daemonset, 灰度, 发版]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# node-agent 灰度发版

## 目标
node-agent 新版本按灰度策略发布到全部集群。

## 适用范围
- 环境：全部集群（6-7 个 DaemonSet，TODO：清单）
- 前提权限：各集群 DaemonSet 修改权

## 前置条件
- 新版本镜像已就绪
- 明确灰度观察指标（节点状态/agent 日志/上报数据）

## 操作步骤

1. 重新部署某个集群的 DaemonSet 作为灰度（TODO：选哪个集群做灰度）
2. 观察灰度集群：节点 Ready、agent 功能正常、无异常日志
3. 确认无问题后，对 6-7 个 DaemonSet 逐个修改发布
4. 每改一个观察一轮再改下一个（TODO：观察时长与指标清单）

## 验证
- 全部集群 DaemonSet 副本数与节点数一致、无 CrashLoop
- agent 上报数据正常

## 回滚
- 将 DaemonSet 镜像改回上一版本 tag，逐集群恢复

## 常见问题
- 某集群升级后异常：立即回滚该集群，保留现场排查

## 关联
- registry：TODO（集群清单台账）
