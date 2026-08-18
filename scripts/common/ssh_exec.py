#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量 VM 执行框架（库，未登记 manifest——供脚本/skill 复用）。
用法见 knowledge/03-构建资源管理/执行资源管理/批量VM操作.md：ip.list + 幂等脚本。
"""
import subprocess
import sys
from pathlib import Path


def ssh_run(host, cmd, password=None, timeout=120):
    """单机执行，返回 (rc, stdout)。password 提供时用 sshpass（密码不落仓，从环境变量取）。"""
    base = ["sshpass", "-p", password, "ssh", "-o", "StrictHostKeyChecking=no", host, cmd] \n        if password else ["ssh", "-o", "BatchMode=yes", host, cmd]
    r = subprocess.run(base, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def batch(ip_file, cmd):
    fails = []
    for ip in Path(ip_file).read_text(encoding="utf-8").splitlines():
        ip = ip.split("#")[0].strip()
        if not ip:
            continue
        rc, out = ssh_run(ip, cmd)
        print(f"[{ip}] rc={rc}")
        if rc != 0:
            fails.append(ip)
            print(out)
    return fails


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("用法: python ssh_exec.py <ip.list> <命令>")
    bad = batch(sys.argv[1], sys.argv[2])
    print(f"
失败 {len(bad)} 台: {bad}")
