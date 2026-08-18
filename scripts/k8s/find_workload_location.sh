#!/usr/bin/env bash
# 按服务名跨命名空间定位 K8s 工作负载 —— manifest: find_workload_location / readonly
# 用法: find_workload_location.sh <服务名关键字>
# 说明: 只读（kubectl get）；找不到时提示 Rancher/VM 侧入口（见 related_doc）。
set -euo pipefail

KW="${1:?用法: $0 <服务名关键字>}"

echo "== Deployment/StatefulSet/DaemonSet 匹配 =="
kubectl get deploy,sts,ds -A -o wide 2>/dev/null | head -1
kubectl get deploy,sts,ds -A -o wide 2>/dev/null | grep -i "$KW" || echo "（无匹配）"

echo; echo "== Service/Ingress 匹配 =="
kubectl get svc,ing -A -o wide 2>/dev/null | grep -i "$KW" || echo "（无匹配）"

echo; echo "== Pod 匹配（前 20） =="
kubectl get pods -A -o wide 2>/dev/null | grep -i "$KW" | head -20 || echo "（无匹配）"

cat <<'TIP'

未命中时（对应手册 knowledge/02-k8s资源管理/定位服务部署位置.md）：
1. Rancher 控制台逐集群/命名空间搜索（入口见 knowledge/02-k8s资源管理/inventory.yaml）
2. VM 部署的服务：登机后 ps -ef | grep <关键字>，再 ls -l /proc/$PID/exe 定位二进制
TIP
