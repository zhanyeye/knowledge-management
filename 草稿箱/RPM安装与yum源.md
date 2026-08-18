---
title: "安装 RPM 包 / 配置 yum 源 / 找基础镜像"
owner: ""
kind: runbook
maturity: draft
risk: medium
tags: [rpm, yum, 镜像, mirrors, vm]
related: []
created: 2026-08-18
last_verified: null
last_reviewed: null
---

# 安装 RPM 包 / 配置 yum 源 / 找基础镜像

## 目标
在内网环境给 vm 装 rpm 包、配 yum 源，或为容器找匹配的微服务基础镜像。

## 适用范围
- 环境：内网 vm / 容器构建
- 前提权限：目标 vm root

## 前置条件
- 确认当前环境 os 类型与版本：
  ```bash
  cat /etc/os-release
  uname -m
  ```

## 操作步骤

1. 到 mirrors.huawei.com 找内网可用源，确认目标库是否在源上
2. 修改环境文件配置源（TODO：repo 文件模板与放置路径待确认）
3. 尝试安装并解决依赖冲突：
   ```bash
   yum install <pkg>
   yum deplist <pkg>    # 依赖冲突分析
   ```
4. 找基础镜像：在镜像仓检索与目标 os 版本匹配的微服务基础镜像（TODO：镜像仓入口）

## 验证
- `rpm -q <pkg>` 或 `yum list installed <pkg>` 确认安装成功
- 基础镜像本地 `docker run --rm <image> cat /etc/os-release` 版本匹配

## 回滚
- 移除新增 repo 文件；`yum remove <pkg>` 卸载（注意依赖连带）

## 常见问题
- 依赖冲突：换更高版本的库源，或找静态编译替代

## 关联
- registry：TODO（mirrors 平台账待建）
