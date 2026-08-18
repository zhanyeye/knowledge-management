---
title: 批量对 VM 执行操作
owner: null
kind: runbook
maturity: draft
risk: high
automation: L0
tags: [批量, vm, shell, sshpass, 高危]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---
# 批量对 VM 执行操作

## 目标
对一批 vm 执行同样的运维命令。**高危：批量放大误操作，先灰度后全量。**

## 适用范围
- 环境：目标 vm 列表
- 前提权限：各 vm 的 ssh 凭证

## 前置条件
- 准备 ip.list（**逐条核对**：主机名/IP/用途/owner）
- 脚本先在 1 台灰度机验证，确认输出符合预期

## 操作步骤

1. 写 shell 脚本（幂等：重复执行不产生副作用；带日志输出）
2. 写 ip.list
3. sshpass 批量执行：
   ```bash
   while read ip; do
     sshpass -p "$PWD_PASS" ssh -o StrictHostKeyChecking=no "$ip" 'bash -s' < ops.sh
   done < ip.list
   ```
   （TODO：凭证来源与安全管理方式——**密码不落仓**）

## 验证
- 逐台检查关键输出/状态符合预期
- 失败清单单独处理，不盲目重跑

## 回滚
- 变更类操作准备反向脚本；不可逆操作（删除）禁用批量执行

## 常见问题
- 个别机器超时：网络/凭证问题单独处理
- 脚本 bug 批量放大：这就是必须灰度先行的原因

## 关联
- registry：TODO（vm 台账，含 owner 字段）
