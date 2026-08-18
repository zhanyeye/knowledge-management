#!/usr/bin/env bash
# 磁盘占用只读扫描 —— manifest 登记: disk_usage_scan / risk_level: readonly
# 用法:
#   disk_usage_scan.sh <host> --quick                     # df 画像，标出超阈值挂载点
#   disk_usage_scan.sh <host> --path <dir> [--depth N]    # 逐层 du 下钻 TOP20
# 说明: 仅执行 df/du 只读命令，不做任何变更；host 为本机时可用 local 代替。
set -euo pipefail

HOST="${1:?用法: $0 <host> (--quick | --path <dir>) [--depth N] [--threshold P]}"
THRESH=85
DEPTH=2
MODE=""
DIR=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --quick)     MODE="quick" ;;
    --path)      MODE="path"; DIR="${2:?--path 需要目录参数}"; shift ;;
    --depth)     DEPTH="$2";   shift ;;
    --threshold) THRESH="$2";  shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -n "$MODE" ] || { echo "必须指定 --quick 或 --path <dir>" >&2; exit 2; }

run() {  # host=local 时本机执行，否则 ssh
  if [ "$HOST" = "local" ]; then bash -c "$1"; else ssh -o BatchMode=yes "$HOST" "$1"; fi
}

case "$MODE" in
  quick)
    echo "== df -h（标出使用率>${THRESH}%） =="
    run "df -hP | awk -v t=$THRESH 'NR==1 || substr(\$5,1,length(\$5)-1)+0>t'"
    echo; echo "== df -i（inode，标出使用率>${THRESH}%） =="
    run "df -iP | awk -v t=$THRESH 'NR==1 || substr(\$5,1,length(\$5)-1)+0>t'"
    echo; echo "== 全量 df -h =="; run "df -h"
    ;;
  path)
    echo "== du 下钻 $DIR (depth=$DEPTH, TOP20) =="
    run "du -h --max-depth=$DEPTH '$DIR' 2>/dev/null | sort -rh | head -20"
    ;;
  *) echo "内部错误: 未知模式 $MODE" >&2; exit 2 ;;
esac
