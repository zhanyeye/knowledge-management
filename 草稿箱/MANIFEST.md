# 草稿箱清单（首次导入：痛点场景表 28 行 → 26 条）

> 来源：`.background/当前痛点场景总结.md`。表格中的原子步骤已填入对应章节；
> 原材料没有的信息（前置/验证/回滚/入口/owner）一律 TODO，**未编造任何内容**。
> review 后逐条转正：`git mv 草稿箱/<文件> <目标路径>` → `python scripts/infra.py index`。
> 转正前建议顺手补 owner 字段（lint 目前只警告不拦截）。

## 排障类 → 排障/（9 条）

| 草稿 | 建议路径 | risk | 主要 TODO |
|---|---|---|---|
| 文件服务器磁盘满.md | 排障/文件服务器磁盘满.md | medium | 受影响服务清单、owner |
| MinIO容量告急.md | 排障/MinIO容量告急.md | medium | 监控入口、mc 命令 |
| 微服务重启分析.md | 排障/微服务重启分析.md | low | ELK/pyroscope 入口、docker 日志路径 |
| Helm部署失败.md | 排障/Helm部署失败.md | medium | pipeline 入口、复现命令模板 |
| 微服务时延大.md | 排障/微服务时延大.md | low | 请求链路图（架构/ 待建） |
| 执行机OOM磁盘满.md | 排障/执行机OOM磁盘满.md | medium | px 任务日志入口 |
| CI任务排队堆积.md | 排障/CI任务排队堆积.md | medium | 队列状态入口 |
| 执行机残留构建失败.md | 排障/执行机残留构建失败.md | medium | 残留目录清单 |
| 数据库负载分析.md | 排障/数据库负载分析.md | low | HIS 慢 SQL 页面入口 |

## 操作类 → 手册/（17 条）

| 草稿 | 建议路径 | risk | 主要 TODO |
|---|---|---|---|
| 定位服务部署位置.md | 手册/k8s/定位服务部署位置.md | low | Rancher 入口与账号 |
| 执行机新增与换镜像.md | 手册/虚机/执行机新增与换镜像.md | medium | 利用率入口、标签规范、viewpoint 入口 |
| 执行机扩缩容.md | 手册/虚机/执行机扩缩容.md | medium | 例会审批材料、参数模板 |
| RPM安装与yum源.md | 手册/虚机/RPM安装与yum源.md | medium | repo 模板、镜像仓入口 |
| 容器镜像制作.md | 手册/发布/容器镜像制作.md | medium | 镜像仓与命名规范 |
| 绿区代理配置.md | 手册/网络/绿区代理配置.md | high | 端口台账、配置路径、reload 方式 |
| node-agent灰度发版.md | 手册/发布/node-agent灰度发版.md | high | 灰度集群选择、观察指标 |
| HIS凭证获取.md | 手册/平台/HIS凭证获取.md | low | HIS 入口、认证方式清单 |
| 域名申请绑定.md | 手册/域名/域名申请绑定.md | medium | DNS 申请流程、配置载体 |
| 客户端证书安装.md | 手册/证书/客户端证书安装.md | low | 证书路径与轮转机制 |
| 服务端证书切换.md | 手册/证书/服务端证书切换.md | high | 申请渠道、挂载点清单 |
| 变更影响排查.md | 手册/网络/变更影响排查.md | low | codesearch 入口 |
| 防火墙申请.md | 手册/网络/防火墙申请.md | low | 电子流入口 |
| 执行机资源清理.md | 手册/虚机/执行机资源清理.md | high | viewpoint 报表入口 |
| 观测组件重启清理.md | 手册/观测/观测组件重启清理.md | high | 各组件日志/数据目录/重启方式 |
| 监控看板搭建.md | 手册/观测/监控看板搭建.md | medium | 服务端仓、配置位 |
| 批量VM操作.md | 手册/虚机/批量VM操作.md | high | 凭证管理方式 |

## 转正后建议的联动（台账优先级）

草稿里反复出现「TODO：xx 入口/台账」，本质是缺台账。建议转正后首批补 10 张：
Rancher（含集群清单）、ROMA、viewpoint、HIS、px 平台、MinIO、镜像仓、ELK、Prometheus/Grafana、Jaeger/Pyroscope。
每张台账的 `knowledge.*` 回填对应手册链接，入口类 TODO 即消灭大半。
