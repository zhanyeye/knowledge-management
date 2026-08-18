#!/usr/bin/env bash
# CI 任务排队/Job 阻塞画像 —— manifest: px_queue_check / readonly
# 用法: px_queue_check.sh [-n 命名空间]
# 说明: kubectl 层面的只读画像；px 平台队列/viewpoint 入口见 inventory（TODO 待补真实入口）。
set -euo pipefail

NS=""
while [ $# -gt 0 ]; do
  case "$1" in
    -n|--namespace) NS="$2"; shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done
KNS=""
[ -n "$NS" ] && KNS="-n $NS"

echo "== 节点压力（MemoryPressure/DiskPressure/PIDPressure） =="
kubectl describe nodes 2>/dev/null | grep -E "^Name:|Pressure:" || true

echo; echo "== 未运行的 Job（排队/阻塞候选） =="
kubectl get jobs $KNS 2>/dev/null | (head -1; awk 'NR>1 && $2 !~ /^[0-9]+\/[0-9]+$/ {print}') || true

echo; echo "== 非 Running Pod 状态分布 =="
kubectl get pods -A 2>/dev/null | awk 'NR>1 && $4!="Running" {print $4}' | sort | uniq -c | sort -rn || true

echo; echo "== Pending Pod（前 15，多为资源不足/ImagePull） =="
kubectl get pods -A 2>/dev/null | awk 'NR>1 && $4=="Pending"' | head -15 || true

cat <<'TIP'
后续（见 knowledge/03-构建资源管理/问题定位/CI任务排队堆积.md）：
1. Pending 因 ImagePull 卡住的 Job → 与属主确认后 kubectl delete job（change，需确认）
2. 找大批量流水线让路 / 扩容走 执行机扩缩容 手册
3. TODO: px 队列状态与 viewpoint 入口（待补进 knowledge/03-构建资源管理/inventory.yaml）
TIP
