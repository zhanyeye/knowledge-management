---
name: infra-locate
description: 基础设施资源定位。当用户问「XX 在哪/部署在哪/哪个环境/谁负责/控制台入口/监控入口/依赖什么」时使用，如 jaeger 生产实例、某域名、某集群、某数据库。查域内 inventory 资产清单给出事实卡。
---

# infra-locate — 资源定位

回答「这个东西在哪、谁负责、怎么进、依赖谁」。

## 流程

1. 查根目录 `域路由表.yaml` 定域（组件类型对不上就先看 INDEX.md 域表）。
2. **Grep** 服务名/域名/组件名，范围优先 `knowledge/<域>/inventory.yaml`；域不确定则 `knowledge/**/inventory.yaml`。
3. 命中则读该台账全文（预算 ≤2 份文件），按下方格式输出事实卡。
4. 台账未命中：Grep `knowledge/`（不限 kind）或读域 INDEX.md。**不要**用 knowhow.py 检索。
5. **台账缺失本身就是发现**：定位成功后把事实补进对应
   `knowledge/<域>/inventory.yaml`（每域一份，多资源列表），提醒用户确认。

## 输出格式

```
<名称>（<env>，criticality）
- 入口：console=… dashboard=… logs=…
- 负责人：team/primary，升级：escalation
- 位置：网络区/集群/命名空间/主机名
- 依赖：upstream → 它 → downstream
- 相关手册：<knowledge.* 链接>
- 置信度：verified/proven 可信；draft 仅供参考
```

## 收尾

命中并使用了资产清单：`python .knowhow/knowhow.py reference knowledge/<域>/inventory.yaml --in "<用户问题>"`。
