# 方案 A：七分区类型制（当前已实现）

> 状态：**已实施**（commit `a3da42d`）。按知识**类型**组织七个分区，源自 `.background/` 专家方案的
> Registry/Runbook/Playbook/ADR/FAQ/Architecture/Incident-case 七类型 + 微信文章三机制。

## 一、当前目录结构（实际状态）

```
knowledge-management/
│
├── AGENTS.md                       # 唯一协作契约（三级索引检索 / 判定表 / 写入规则 / risk 分级 / 治理）
├── README.md                       # 人的入口
├── INDEX.md                        # 一级索引【自动生成】
│
├── 台账/                           # 资产台账（YAML，按对象类型分子目录）
│   ├── 集群/ 数据库/ 中间件/ 域名/ 证书/ 存储/ 观测/ 平台/ 服务/ 虚机/
│   └── （全部为空，.gitkeep 占位）
│
├── 手册/                           # 操作手册（按动作组织，按域分子目录）
│   └── k8s/ 网络/ 域名/ 证书/ 虚机/ 发布/ 数据库/ 观测/ 平台/（空）
│
├── 排障/                           # 排障手册（按症状组织，平铺）
├── 决策/                           # ADR（空）
├── 问答/                           # FAQ（空）
├── 架构/                           # 拓扑/请求链路/数据流（空）
├── 案例/                           # 故障复盘，按年（空）
│
├── 草稿箱/                         # ★ 新知识唯一写入口（26 条草稿待人工 review 转正）
│   ├── MANIFEST.md                 # 草稿清单 + 建议转正路径 + 主要 TODO
│   └── 文件服务器磁盘满.md 等 26 条 # 痛点场景表 28 行导入：9 排障 + 17 操作
│
├── 归档/                           # 衰减归档（decay --fix 执行，可逆）
│
├── templates/                      # 八套模板：runbook / playbook / adr / faq /
│                                   #   incident-case / architecture-note / registry-resource / checklist
├── scripts/
│   ├── infra.py                    # 引擎：index / search / lint / decay / reference / verify / new
│   ├── infra.json                  # 配置：预算 / 衰减阈值 / lint 规则
│   └── test_infra.py               # 单测（18 个）
│
├── .claude/skills/                 # 四个任务入口
│   ├── infra-locate/               # 资源定位 → 查台账
│   ├── infra-change/               # 变更指引 → 查手册 + risk 分级执行
│   ├── infra-troubleshoot/         # 排障 → 查排障分区
│   └── infra-import/               # 导入整理 → 草稿箱暂存
│
├── .infra/                         # refs-YYYY.jsonl 引用旁车 + log-YYYY.md 操作日志
└── .background/                    # 设计资料
```

## 二、工作流

```
写入：infra.py new <kind> <名> → 草稿箱/（maturity=draft）
      → AI/人补内容（禁止编造，缺项 TODO）→ lint 零错误
      → 人工 review → git mv 草稿箱/<文件> <分区>/ → index → commit

检索：INDEX.md（总）→ 分区 INDEX.md（二级）→ 按预算读全文
      辅助：infra.py search <关键词>（标题×4 标签×3 H2×2 正文×1 加权）

治理：三级成熟度 draft→verified→proven；手册/排障 6 个月无引用自动降级；
      draft 归档需 decay --fix；台账靠 last_reviewed 90 天告警；lint 校验
      kind↔目录 / related 链接 / 模板章节 / registry 必填字段
```

## 三、A / B 方案对比

| 维度 | 方案 A（当前·类型制） | 方案 B（设计·域制） |
|---|---|---|
| 组织维度 | 先按**类型**（7 个顶层分区），域在二级 | 先按**层**（knowledge 事实 / runbooks 程序 / adr），域在二级 |
| 「查 Mongo 连接超时」路径 | search → 排障/（平铺，靠 tags）→ 命中后查 台账/数据库/ 找实例 | runbooks/database/ 目录直接翻 + knowledge/database/inventory.yaml 拿实例 |
| 「Mongo 的一切」聚合度 | 分散在 台账/手册/排障/问答/架构/案例 六处 | runbooks/database/ + knowledge/database/ 两处 |
| 台账形态 | 一对象一文件（台账/数据库/mongo-x.yaml） | 一域一文件多资源（inventory.yaml 列表） |
| 写入流程 | 草稿箱暂存 → 人审 git mv 转正（多一步，已被评为上手负担） | 直接写目标位置 + maturity=draft，git diff 即评审 |
| 归档 | 归档/ 目录 + decay --fix | 无归档目录，decay 报「建议删除」，git 历史兜底 |
| 自动化深度 | 4 个任务 skill（知识检索/指引型） | 同样 4 个 + **原子 skill 模式**（SKILL.md+scripts+references，脚本可执行） |
| 执行留痕 | .infra/refs 引用旁车 + 操作日志 | 同左 + reports/ 诊断报告落盘 |
| CI | 无 | lint + 单测 workflow |
| 目录命名 | 中文两字（台账/手册/排障…，已被评为歧义/糟糕） | 英文行业词 + 中文文件名（FAQ/ADR/runbook） |
| 引擎改动 | 无（现状） | 中等：kind→顶层映射改域制、文件名规则、去草稿箱/归档逻辑 |
| 术语表 | 无 | knowledge/glossary.md |

## 四、各自适合的场景

- **方案 A** 更适合：知识量小、类型差异比领域差异更重要、希望每种文档结构高度统一（lint 按类型查模板最直接）
- **方案 B** 更适合：以「组件/平台」为工作中心（你们的痛点表全是「px 执行机/HIS/MinIO」域式提问）、
  想逐步沉淀可执行脚本自动化（你们最初的目标）、团队习惯 git 评审而不想要额外暂存流程
