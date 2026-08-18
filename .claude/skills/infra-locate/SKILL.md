---
name: infra-locate
description: 基础设施资源定位。当用户问「XX 在哪/部署在哪/哪个环境/谁负责/控制台入口/监控入口/依赖什么」时使用，如 jaeger 生产实例、某域名、某集群、某数据库。查台账（registry）给出事实卡。
---

# infra-locate — 资源定位

回答「这个东西在哪、谁负责、怎么进、依赖谁」。

## 流程

1. 优先查台账：
   ```bash
   python scripts/infra.py search <服务名/域名/组件名> --kind registry --limit 3
   ```
   命中则读对应 YAML 全文（预算 ≤2 条）。
2. 台账未命中时降级：`search <关键词> --limit 5`（不限 kind），或读 `INDEX.md` 换关键词重试。
3. **台账缺失本身就是发现**：定位成功（从人/群聊/其他途径得知）后，把事实补成
   `python scripts/infra.py new registry <名称>` 草稿，提醒用户确认转正。

## 输出格式

```
<名称>（<env>，criticality）
- 入口：console=… dashboard=… logs=…
- 负责人：team/primary，升级：escalation
- 位置：网络区/集群/命名空间/主机名
- 依赖：upstream → 它 → downstream
- 相关手册：<knowledge.* 链接>
- 置信度：<verified/proven 可信；draft 仅供参者>
```

## 收尾

命中并使用了台账：`python scripts/infra.py reference 台账/<类型>/<名称>.yaml --in "<用户问题>"`。
