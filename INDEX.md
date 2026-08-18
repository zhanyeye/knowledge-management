# 基础设施知识库 · 总索引

> 自动生成于 2026-08-18，共 26 条。查询协议：本文件 → 目录 INDEX.md → 按预算读条目全文（预算见 scripts/infra.json）。

| 分区 | 装什么 | 条数 | draft/verified/proven |
|---|---|---|---|
| [台账/](台账/INDEX.md) | 资产台账：对象事实卡（在哪/谁负责/入口） | 0 | 0/0/0 |
| [手册/](手册/INDEX.md) | 操作手册：这件事怎么做、怎么回滚 | 0 | 0/0/0 |
| [排障/](排障/INDEX.md) | 排障手册：这个症状怎么查 | 0 | 0/0/0 |
| [决策/](决策/INDEX.md) | 决策记录：为什么这样设计 | 0 | 0/0/0 |
| [问答/](问答/INDEX.md) | 高频问答：1 分钟短答案 | 0 | 0/0/0 |
| [架构/](架构/INDEX.md) | 架构说明：链路/拓扑/数据流 | 0 | 0/0/0 |
| [案例/](案例/INDEX.md) | 故障复盘：真实案例怎么定位的 | 0 | 0/0/0 |

## 草稿箱（待人工确认的草稿）

- **[px 执行资源排队堆积](草稿箱/CI任务排队堆积.md)** · playbook · draft · risk:medium · #px #ci #排队 #资源
- **[HIS API 订阅与 appkey/token 获取](草稿箱/HIS凭证获取.md)** · runbook · draft · risk:low · #his #appkey #token #订阅 #凭证
- **[Helm 部署失败排查](草稿箱/Helm部署失败.md)** · playbook · draft · risk:medium · #helm #发布 #k8s #排障
- **[MinIO 存储空间/inode 快满](草稿箱/MinIO容量告急.md)** · playbook · draft · risk:medium · #minio #存储 #容量 #磁盘
- **[安装 RPM 包 / 配置 yum 源 / 找基础镜像](草稿箱/RPM安装与yum源.md)** · runbook · draft · risk:medium · #rpm #yum #镜像 #mirrors #vm
- **[node-agent 灰度发版](草稿箱/node-agent灰度发版.md)** · runbook · draft · risk:high · #node-agent #daemonset #灰度 #发版
- **[周边服务变更影响排查（证书/IAM 切换）](草稿箱/变更影响排查.md)** · runbook · draft · risk:low · #影响面 #变更 #codesearch #证书 #iam
- **[微服务域名新增申请与 nginx 配置部署](草稿箱/域名申请绑定.md)** · runbook · draft · risk:medium · #域名 #dns #nginx #负载均衡 #路由
- **[定位服务部署位置（Rancher 负载 / VM 进程）](草稿箱/定位服务部署位置.md)** · runbook · draft · risk:low · #定位 #rancher #k8s #vm #进程
- **[HTTPS 客户端证书安装](草稿箱/客户端证书安装.md)** · runbook · draft · risk:low · #证书 #客户端 #https #dockerfile
- **[微服务容器镜像制作](草稿箱/容器镜像制作.md)** · runbook · draft · risk:medium · #镜像 #dockerfile #构建 #微服务
- **[微服务响应时延大（逐层定位）](草稿箱/微服务时延大.md)** · playbook · draft · risk:low · #时延 #性能 #网络 #排障
- **[微服务重启原因分析（找日志）](草稿箱/微服务重启分析.md)** · playbook · draft · risk:low · #k8s #重启 #oom #日志 #排障
- **[px 执行机 OOM/磁盘满定位](草稿箱/执行机OOM磁盘满.md)** · playbook · draft · risk:medium · #px #执行机 #oom #磁盘 #ci
- **[px 容器资源宿主机扩缩容](草稿箱/执行机扩缩容.md)** · runbook · draft · risk:medium · #px #扩容 #缩容 #roma #资源
- **[px 虚机新增执行机 / 更换执行机镜像](草稿箱/执行机新增与换镜像.md)** · runbook · draft · risk:medium · #px #执行机 #镜像 #viewpoint
- **[执行机残留导致构建失败](草稿箱/执行机残留构建失败.md)** · playbook · draft · risk:medium · #px #执行机 #构建失败 #残留
- **[viewpoint 执行机延期/关机资源清理](草稿箱/执行机资源清理.md)** · runbook · draft · risk:high · #viewpoint #执行机 #清理 #资产
- **[批量对 VM 执行操作](草稿箱/批量VM操作.md)** · runbook · draft · risk:high · #批量 #vm #shell #sshpass #高危
- **[数据库负载问题分析](草稿箱/数据库负载分析.md)** · playbook · draft · risk:low · #数据库 #慢sql #负载 #his #排障
- **[公共/px 文件服务器磁盘满](草稿箱/文件服务器磁盘满.md)** · playbook · draft · risk:medium · #磁盘 #文件服务器 #vm #存储
- **[HTTPS 服务端证书切换](草稿箱/服务端证书切换.md)** · runbook · draft · risk:high · #证书 #轮换 #https #高危
- **[监控看板搭建（Grafana/PromQL 与 Metabase/SQL）](草稿箱/监控看板搭建.md)** · runbook · draft · risk:medium · #grafana #prometheus #metabase #看板 #监控
- **[配置绿区转发代理](草稿箱/绿区代理配置.md)** · runbook · draft · risk:high · #代理 #nginx #haproxy #绿区 #网络
- **[观测组件重启/磁盘清理（pyroscope/jaeger/es/prometheus）](草稿箱/观测组件重启清理.md)** · runbook · draft · risk:high · #观测 #重启 #磁盘清理 #prometheus #jaeger #es #pyroscope
- **[防火墙开通申请](草稿箱/防火墙申请.md)** · runbook · draft · risk:low · #防火墙 #网络 #申请 #审批

> 确认后 `git mv 草稿箱/<文件> <目标分区>/` 并重跑 `python scripts/infra.py index`。

## 按任务类型的查询预算

- **troubleshoot**: 排障：先查 playbook，再查 registry 定位资源（目录≤2，全文≤3）
- **ops_execute**: 执行手册：完整读目标 runbook；risk=high 必须人工逐项确认（目录≤1，全文≤1）
- **locate**: 资源定位：以 registry 台账为主（目录≤2，全文≤2）
- **default**: 默认预算（目录≤2，全文≤5）
