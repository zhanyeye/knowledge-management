---
name: infra-troubleshoot
description: 基础设施故障排查。当用户描述症状/异常时使用：磁盘满、OOM、Pod CrashLoop/Pending、502/504、超时、慢查询、指标/日志/trace 缺失、发布失败、队列堆积等。查 playbook 按排查树定位。
---

# infra-troubleshoot — 故障排查

「出了这个症状，先查什么、再查什么、什么时候升级」。

## 流程

1. 提取症状关键词，找排障手册：
   ```bash
   python scripts/infra.py search <症状关键词> --kind playbook --limit 3   # 结果在 排障/
   ```
2. **完整读命中的 playbook**（预算 ≤3 条），按排查路径顺序执行：
   - 只读诊断命令（kubectl get/describe/logs/events、top、df、du、看面板/日志检索）视为 **low，直接执行**并汇报判读结果；
   - 变更类动作（delete/restart/清理/改配置）按其所属 runbook 的 risk 分级处理（medium 逐项确认、high 只出指引）。
3. 涉及具体资源用 `infra-locate` 定位（哪个集群/实例/入口）。
4. 命中根因并解决 → 收尾；排查树走完未解决 → 见「升级」。

## 升级

playbook 的「升级条件」节指明何时停止自查、找谁。没有写明的：报告已排除的路径 + 当前证据，建议联系资源 owner（查 registry）。

## 收尾（两件事）

1. `python scripts/infra.py reference <playbook路径> --in "<故障简述>"`；
2. 本次走了新路径/发现手册没覆盖的根因 → 用 infra-import 流程把这次的排查步骤补进 playbook 或沉淀新 playbook/case。**排障经验不沉淀，下次还得从零查。**
