# 修改后的完整目录结构

```
infra-knowledge/
│
├─ CLAUDE.md                          # 全局入口：域路由表、agent行为规范、目录使用说明
├─ FAQ.md                             # 高频问答速查
├─ 常用链接.md
├─ 问题定位索引.md                    # 症状关键词 → 域 → 文档路径（跨域路由，见下方示例）
├─ 域路由表.yaml                      # CLAUDE.md引用的结构化版本，agent优先查这个而非记路径
│
├─ knowledge/                         # ============ 知识库主体 ============
│  │
│  ├─ 00-通用环境基线/                 # 原Linux&容器基础，大幅精简，只留内部特有约定
│  │  ├─ 内部OS与镜像基线.md          # 只写"我们跟标准Linux不同的地方"，通用命令不再重复
│  │  ├─ 卷与磁盘挂载规范.md          # 内部数据盘命名/挂载约定
│  │  └─ docker运行时约定.md          # 内部docker配置差异点（如有）
│  │
│  ├─ 01-镜像制作/
│  │  ├─ 统一镜像制作.md
│  │  ├─ 微服务镜像制作.md
│  │  ├─ 镜像仓管理/
│  │  │  ├─ harbor镜像仓清理.md
│  │  │  └─ 内网下载dockerhub开源镜像.md
│  │  └─ 问题定位/
│  │     └─ 镜像制作常见问题.md
│  │
│  ├─ 02-k8s资源管理/
│  │  ├─ k8s基础与内部约定.md         # 只写内部命名/标签规范，非k8s教程
│  │  ├─ 服务器资源/
│  │  │  └─ 节点资源管理.md
│  │  ├─ 可观测/
│  │  │  └─ 监控告警.md
│  │  ├─ 版本发布/
│  │  │  ├─ 基于Helm的微服务发布部署.md
│  │  │  ├─ 开源Helm相关.md
│  │  │  └─ node-agent发版.md
│  │  ├─ 集群管理/
│  │  │  ├─ 导入集群至Rancher.md
│  │  │  ├─ Rancher部署.md
│  │  │  └─ RancherUI登录问题.md
│  │  └─ 问题定位/
│  │     ├─ Rancher服务负载查找.md
│  │     ├─ 微服务重启OOM分析.md
│  │     └─ Helm部署失败排查.md
│  │
│  ├─ 03-构建资源管理/
│  │  ├─ ROMA/
│  │  │  ├─ roma操作.md
│  │  │  └─ roma资源轮换.md
│  │  ├─ HIS/
│  │  │  └─ HIS构建基础.md
│  │  ├─ 云龙/
│  │  │  ├─ 云龙api非标调用整改.md
│  │  │  ├─ 云龙api-Px细节说明.md
│  │  │  └─ 云龙容器构建问题汇总.md
│  │  ├─ PipelineX/
│  │  │  ├─ Gate使用说明.md
│  │  │  ├─ 版本构建集群宿主机升级.md
│  │  │  └─ minio缓存获取非最新问题.md
│  │  ├─ 门禁Gate/
│  │  │  ├─ 门禁增量重试功能-CI工程适配规范.md
│  │  │  ├─ 门禁重试增量执行.md
│  │  │  └─ 编码门禁修复.md
│  │  ├─ 执行资源管理/
│  │  │  ├─ 执行资源迁移芜湖地域分析.md
│  │  │  ├─ 执行机低利用率替换镜像.md
│  │  │  ├─ 门禁执行机对接云龙vpc.md
│  │  │  └─ viewpoint执行机延期关机清理.md
│  │  ├─ 改进复盘/                    # 沉淀类，非SOP
│  │  │  ├─ gollt时长优化2024.md
│  │  │  └─ pipelinex执行goLLT时长优化改进.md
│  │  └─ 问题定位/
│  │     ├─ px白名单速度问题.md
│  │     ├─ px执行资源排队问题.md
│  │     ├─ 执行机残留数据导致构建失败.md
│  │     └─ px任务执行机oom磁盘满定位.md
│  │
│  ├─ 04-网络管理/
│  │  ├─ DNS域名解析/
│  │  │  ├─ 内网域名申请.md
│  │  │  └─ DNS修改.md
│  │  ├─ https证书管理/
│  │  │  ├─ https证书基础知识.md
│  │  │  ├─ https证书新增.md
│  │  │  ├─ https证书替换.md
│  │  │  └─ https客户端证书安装.md
│  │  ├─ 网络防火墙/
│  │  │  └─ 防火墙申请流程.md
│  │  ├─ 代理网关/
│  │  │  ├─ 通用区haproxy.md
│  │  │  ├─ nginx配置.md
│  │  │  ├─ 通用区网关配置.md
│  │  │  ├─ 绿区转发代理配置.md
│  │  │  └─ k8s的nginx负载均衡问题.md
│  │  └─ 问题定位/
│  │     ├─ 周边服务变更影响排查.md   # https/iam切换类
│  │     └─ 微服务响应时延链路排查.md
│  │
│  ├─ 05-数据库/
│  │  ├─ HIS数据库/
│  │  │  └─ HIS数据库基础.md
│  │  ├─ 自建数据库/
│  │  │  ├─ clickhouse.md
│  │  │  ├─ clickhouse表清理.md
│  │  │  └─ openGauss数据库切换.md
│  │  └─ 问题定位/
│  │     ├─ mongo问题.md
│  │     └─ 数据库负载问题分析.md
│  │
│  ├─ 06-存储/
│  │  ├─ Minio对象存储/
│  │  │  ├─ Minio概述与搭建.md
│  │  │  ├─ Minio集群搭建.md
│  │  │  ├─ Minio性能问题.md
│  │  │  └─ minio负载均衡与可靠性分析.md
│  │  └─ 问题定位/
│  │     ├─ px公共文件服务器满问题.md
│  │     └─ minio存储空间inode快满.md
│  │
│  ├─ 07-消息中间件/
│  │  └─ 问题定位/
│  │     └─ mq消费延迟问题.md
│  │
│  ├─ 08-数据工程与AI平台/
│  │  ├─ AI-mlops/
│  │  │  ├─ 镜像接入.md
│  │  │  ├─ 多训练平台管理.md
│  │  │  ├─ 模型服务设计.md
│  │  │  └─ 方案设计/                 # RFC类归档，非SOP
│  │  │     ├─ 流水线重构-详细方案.md
│  │  │     └─ 流水线重构-现状修改点分析.md
│  │  ├─ 数据工程/
│  │  │  ├─ 数据工程总览.md
│  │  │  ├─ 数据质检-规则描述.md
│  │  │  ├─ 数据集管理.md
│  │  │  ├─ app属性版本管理.md
│  │  │  └─ ydata-profiling使用.md
│  │  ├─ 数据飞轮/
│  │  │  ├─ 测试集自动验证.md
│  │  │  ├─ 模型训练自动化.md
│  │  │  └─ 数据治理-界面与需求分析.md
│  │  ├─ 特征工程与可视化/
│  │  │  └─ 数据特征降维可视化.md
│  │  └─ 问题定位/
│  │     └─ 数据回传NFS卡住问题.md
│  │
│  ├─ 09-业务平台对接/                 # 内部专有系统代号类
│  │  ├─ FOA与珊瑚.md
│  │  ├─ 珊瑚网元环境任务调度子系统设计.md
│  │  ├─ 扶摇2.0对接AI-bom需求方案.md
│  │  ├─ deployer切换珊瑚指导书.md
│  │  ├─ IPE蓝区演示前后端设计方案.md
│  │  └─ IPE客户效果体验测试系统方案.md
│  │
│  └─ 10-研发效能与协同/
│     ├─ 切换工号继承问题.md
│     ├─ AI辅助代码生成.md
│     └─ 子agent能力验证.md
│
├─ scripts/                           # ============ 自动化脚本区 ============
│  ├─ manifest.yaml                   # 脚本清单：见下方示例，agent优先查这个
│  ├─ common/
│  │  ├─ ssh_exec.py                  # 批量VM执行框架
│  │  ├─ kube_client.py
│  │  └─ notify_slack.py
│  ├─ os/
│  │  ├─ install_compiler.sh          # 毕昇编译器安装
│  │  └─ disk_cleanup.sh              # 提升磁盘空间使用率脚本
│  ├─ k8s/
│  │  ├─ find_workload_location.sh    # 查找rancher服务负载位置
│  │  └─ diagnose_pod_oom.sh
│  ├─ build/
│  │  ├─ px_low_utilization_finder.py # 找低利用率VM
│  │  ├─ px_queue_check.sh
│  │  └─ executor_residue_cleanup.sh
│  ├─ network/
│  │  └─ cert_rotation.sh
│  ├─ db/
│  │  └─ slow_query_check.py
│  ├─ storage/
│  │  ├─ disk_usage_scan.sh           # du分层扫描找大文件
│  │  └─ minio_lifecycle_config.py
│  └─ data-eng/
│     └─ nfs_hang_diagnose.sh
│
├─ .claude/
│  ├─ settings.json
│  ├─ skills/                         # 按域二级分类
│  │  ├─ k8s/
│  │  │  ├─ find-workload-location/SKILL.md
│  │  │  └─ node-scaling/SKILL.md
│  │  ├─ build/
│  │  │  ├─ px-executor-rotation/SKILL.md
│  │  │  └─ px-queue-troubleshoot/SKILL.md
│  │  ├─ storage/
│  │  │  └─ disk-space-cleanup/SKILL.md
│  │  ├─ db/
│  │  │  └─ slow-query-diagnosis/SKILL.md
│  │  └─ network/
│  │     └─ cert-rotation/SKILL.md
│  ├─ agents/
│  └─ hooks/
│     ├─ pre-apply-guard.sh           # 变更类操作二次确认
│     └─ post-tool-use-log.sh         # 执行记录回填runbooks/history
│
├─ runbooks/history/                  # agent执行历史自动追加
├─ reports/                           # 定时巡检/诊断报告
├─ tests/skills/
└─ .github/workflows/
   ├─ daily-inventory-sync.yml
   └─ doc-script-link-check.yml       # 校验文档↔脚本↔manifest三者链接不失效
```

## 几个配套文件的示例内容

**`问题定位索引.md`（根目录，跨域症状路由）**

```markdown
| 症状关键词 | 涉及域 | 详细文档 | 对应脚本 |
|---|---|---|---|
| 磁盘满/inode满 | 存储/构建资源 | knowledge/06-存储/问题定位/px公共文件服务器满问题.md | scripts/storage/disk_usage_scan.sh |
| OOM/进程被kill | k8s/构建资源 | knowledge/02-k8s.../微服务重启OOM分析.md | scripts/k8s/diagnose_pod_oom.sh |
| 找服务部署位置 | k8s/VM | knowledge/02-k8s.../Rancher服务负载查找.md | scripts/k8s/find_workload_location.sh |
| 执行资源排队 | 构建资源 | knowledge/03-.../问题定位/px执行资源排队问题.md | scripts/build/px_queue_check.sh |
```

**`scripts/manifest.yaml`**

```yaml
- name: disk_usage_scan
  domain: storage
  path: scripts/storage/disk_usage_scan.sh
  description: 分层扫描目录找出磁盘占用最大的文件/目录
  risk_level: readonly
  entry_command: "bash disk_usage_scan.sh <path> [--depth N]"
  related_doc: knowledge/06-存储/问题定位/px公共文件服务器满问题.md

- name: px_low_utilization_finder
  domain: build
  path: scripts/build/px_low_utilization_finder.py
  description: 扫描px执行机集群，找出低利用率VM供镜像替换/回收
  risk_level: readonly
  entry_command: "python px_low_utilization_finder.py --cluster <name>"
  related_doc: knowledge/03-构建资源管理/执行资源管理/执行机低利用率替换镜像.md

- name: executor_residue_cleanup
  domain: build
  path: scripts/build/executor_residue_cleanup.sh
  risk_level: change          # 变更类，需走hooks确认
  entry_command: "bash executor_residue_cleanup.sh <node> [--dry-run]"
  related_doc: knowledge/03-构建资源管理/问题定位/执行机残留数据导致构建失败.md
```

**`域路由表.yaml`（根目录，替代agent"记编号"）**

```yaml
domains:
  k8s: knowledge/02-k8s资源管理
  build: knowledge/03-构建资源管理
  network: knowledge/04-网络管理
  db: knowledge/05-数据库
  storage: knowledge/06-存储
  mq: knowledge/07-消息中间件
  data-ai: knowledge/08-数据工程与AI平台
```

## 关键变化说明

1. **叶子文档全部去序号**，用语义文件名；顶层域保留序号（人读方便），但agent实际寻址靠`域路由表.yaml`，不靠记编号。
2. **`00-Linux&容器基础`降级为`00-通用环境基线`**，内容从"教程"压缩为"内部特有约定"，篇幅应该比原来少70%以上。
3. **问题定位保留域内详细文档，但新增根目录索引做跨域路由**，两层结构兼顾"精确排查"和"模糊症状分发"。
4. **脚本按域分类存放，配合`manifest.yaml`统一登记**，文档和脚本互相在文末/头部注释链接，CI里加了`doc-script-link-check.yml`防止链接腐化。
5. **方案设计类文档单独子目录归档**（如`AI-mlops/方案设计/`），跟可执行SOP区分，避免agent把"决策记录"误当成"操作步骤"去执行。
