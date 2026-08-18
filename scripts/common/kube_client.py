#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kubectl 薄封装（库，未登记 manifest）。统一超时/错误处理，供脚本复用。"""
import subprocess


def kubectl(*args, timeout=60):
    r = subprocess.run(["kubectl", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"kubectl {