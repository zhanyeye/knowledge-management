---
name: infra-troubleshoot
description: 基础设施故障排查。当用户描述症状/异常时使用：磁盘满、OOM、Pod CrashLoop/Pending、502/504、超时、慢查询、指标/日志/trace 缺失、发布失败、队列堆积等。先查问题定位索引，按排查路径执行，结论写 reports/。
---

# infra-troubleshoot — 故障排查

「出了这个症状，先查什么、再查什么、什么时候升级」。

## 流程

1. **先读 问题定位索引.md**（根目录，症状→域→文档→脚本→skill）：
   - 命中且有 skill → 直接用该 skill（如 storage/disk-usage-diagnose）
   - 命中有脚本（manifest risk_level: readonly）→ 直接跑脚本拿画像
2. 索引未命中：`python scripts/infra.py search <症状关键词> --kind playbook --limit 3`
3. **完整读命中的问题定位文档**（预算 ≤3 条），按排查路径顺序执行；
   涉及资源用 infra-locate 查 inventory。
4. 变更类动作（delete/restart/清理）按 infra-change 的三层闸门——排障中也不豁免。
5. 排查树走完未解决 → 见文档「升级条件」；没写的报告已排除路径+当前证据，找资源 owner。

## 收尾（三件事）

1. `python scripts/infra.py reference <文档路径> --in "<故障简述>"`
2. 结论写 `reports/YYYY-MM-<主题>.md`：现象/排查路径/根因/处置/遗留
3. 走了新路径或发现手册没覆盖的根因 → 直接把这次的排查步骤补进对应 问题定位/ 文档
   （标 symptoms），或沉淀新 playbook/复盘。**经验不沉淀，下次从零查。**
