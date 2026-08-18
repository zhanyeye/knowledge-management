#!/usr/bin/env bash
# Pod 重启/OOM 只读诊断 —— manifest: diagnose_pod_oom / readonly
# 用法: diagnose_pod_oom.sh <pod名> [-n 命名空间]
# 输出: 重启计数/原因、上次容器日志尾部、宿主机 dmesg OOM 线索、后续排查建议。
set -euo pipefail

POD="${1:?用法: $0 <pod名> [-n 命名空间]}"
NS=""
shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    -n|--namespace) NS="$2"; shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done
KNS=""
[ -n "$NS" ] && KNS="-n $NS"

echo "== Pod 概览（RESTARTS / 状态） =="
kubectl get pod $KNS -o wide 2>/dev/null | (head -1; grep "$POD") || echo "（未找到 pod）"

echo; echo "== lastState（退出码/OOM 判定关键） =="
kubectl get pod $KNS -o jsonpath='{range .items[?(@.metadata.name=="'"$POD"'")]}{range .status.containerStatuses[*]}{.name}{"  restarts="}{.restartCount}{"  lastState="}{.lastState}{"\n"}{end}{end}' 2>/dev/null || true

echo; echo "== 上次崩溃日志（--previous 尾 30 行） =="
kubectl logs "$POD" $KNS --previous --tail=30 2>&1 | tail -30 || true

echo; echo "== 事件（近 10 条） =="
kubectl get events $KNS --field-selector involvedObject.name="$POD" 2>/dev/null | tail -10 || true

cat <<'TIP'

dmesg 层确认（需登宿主机，只读）：
  dmesg -T | grep -i -E "oom|kill" | tail -20
内存画像：pyroscope 入口见 knowledge/02-k8s资源管理/inventory.yaml（可观测资源）
完整排查树：knowledge/02-k8s资源管理/问题定位/微服务重启分析.md
TIP
