---
title: Helm 部署失败排查
owner: null
kind: playbook
maturity: draft
risk: medium
automation: L0
symptoms: [helm部署失败, 发布失败, 部署超时]
tags: [helm, 发布, k8s, 排障]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# Helm 部署失败排查

## 症状
- 表现：流水线 Helm 部署失败/超时
- 影响面初判：该服务发布受阻

## 排查路径

### 1. 流水线日志找请求报错与版本
- 看 pipeline 日志中的请求报错、部署的版本号（TODO：pipeline 入口）

### 2. 看 Helm 报错并复现
- 查看 helm 报错信息与当前 helm 配置
- 手动执行 helm 命令复现（TODO：待确认的复现命令模板——建议 dry-run 先行）

### 3. 对照 k8s 负载查模板不匹配/冲突
- 到 k8s 对应负载处查看：k8s 组件与 helm 模板不匹配 / 资源冲突
  ```bash
  kubectl get deploy,svc,ingress -n <ns>
  kubectl describe <资源> -n <ns>
  ```

## 常见根因

| 根因 | 特征 | 处理 |
|---|---|---|
| 模板与集群现状冲突 | 已存在同名资源 | 清理或改名 |
| TODO | | |

## 升级条件
- 涉及共享组件（ingress/configmap）冲突：找平台 owner 确认再动

## 关联
- runbook：TODO（helm-CD 发布流程）
