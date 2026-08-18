---
title: HIS API 订阅与 appkey/token 获取
owner: null
kind: runbook
maturity: draft
risk: low
automation: L0
tags: [his, appkey, token, 订阅, 凭证]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# HIS API 订阅与 appkey/token 获取

## 目标
为团队/应用获取 HIS 平台的 API 订阅凭证（appkey/token）。

## 适用范围
- 环境：HIS 平台
- 前提权限：HIS 登录与订阅权限

## 前置条件
- 明确团队/应用身份：**团队与应用的 key 有差别，且存在多种认证方式**（TODO：认证方式清单）

## 操作步骤

1. 找历史代码配置/管理员确认该用的认证方式与历史 key
2. 登录 HIS 查找对应凭证（TODO：HIS 入口与具体页面路径）
3. 手动获取并保存（**禁止入库任何凭据明文**；保存位置 TODO：确认团队凭证管理方式）

## 验证
- 用获取的 appkey/token 调一次目标 API 返回正常

## 回滚
- 凭证获取失败不影响存量；错误凭证作废即可

## 常见问题
- 认证方式选错：对照步骤 1 确认团队 key 与应用 key 的差别

## 关联
- faq：TODO（建议补一条「his 的 appkey 去哪拿」短问答）
