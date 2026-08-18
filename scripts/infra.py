#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""infra.py — 基础设施知识库引擎（纯标准库，零依赖）· 方案D域制结构

子命令：
  index                    生成 INDEX.md（总）+ 域 INDEX.md + 问题定位索引.md + 域路由表.yaml
  search <词...>           加权检索（标题x4 tagsx3 H2x2 正文x1），--kind 过滤
  lint                     结构/链接/manifest/自动化标注治理，错误时退出码 1
  decay                    成熟度衰减（verified 6月无信号降 draft；draft 闲置报删除建议）
  reference <路径...>      记引用（写 .infra/refs-YYYY.jsonl，不改条目）
  verify <路径>            升成熟度 / inventory 复审（last_reviewed）
  new <kind> <名>          按模板生成到目标域（--domain 必填）

约定见 AGENTS.md；配置 scripts/infra.json；脚本登记表 scripts/manifest.yaml。
"""
import argparse
import getpass
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KINDS = ("registry", "runbook", "playbook", "adr", "faq", "architecture", "case", "reference")
KIND_DESC = {
    "registry": "台账：inventory.yaml 资源事实卡",
    "runbook": "操作手册：这件事怎么做、怎么回滚",
    "playbook": "排障手册：这个症状怎么查（问题定位/）",
    "adr": "决策/方案记录：为什么这样设计（方案设计/）",
    "faq": "高频问答：1 分钟短答案",
    "architecture": "架构说明：链路/拓扑（mermaid）",
    "case": "复盘：真实案例怎么定位的（复盘/）",
    "reference": "基线/约定：只写内部特有约定",
}
KIND_TEMPLATES = {
    "registry": "inventory.yaml", "runbook": "runbook.md", "playbook": "playbook.md",
    "case": "incident-case.md", "adr": "adr.md", "faq": "faq.md",
    "architecture": "architecture.md", "reference": "reference.md",
}
SKIP_FILES = {"INDEX.md", "MANIFEST.md", "README.md", "glossary.md"}


def out(s=""):
    print(s)


def die(msg, code=1):
    out(f"[infra] 错误: {msg}")
    sys.exit(code)


def config_path():
    return ROOT / "scripts" / "infra.json"


def load_config():
    p = config_path()
    if not p.exists():
        die(f"缺少配置文件 {p.as_posix()}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        die(f"infra.json 格式错误（第 {ex.lineno} 行第 {ex.colno} 列）: {ex.msg}")
        return None


def today_str():
    return date.today().isoformat()


def parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def months_between(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def os_user():
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


# ---------------------------------------------------------- frontmatter（扁平子集）

def _split_top(s):
    parts, depth, buf = [], 0, []
    for ch in s:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def _parse_scalar(raw):
    s = raw.strip()
    if s in ("", "null", "~", '""', "''"):
        return None
    if s.startswith("[") and s.endswith("]"):
        return [_parse_scalar(p) for p in _split_top(s[1:-1].strip())]
    if s.startswith("{") and s.endswith("}"):
        d = {}
        for part in _split_top(s[1:-1].strip()):
            if ":" in part:
                k, v = part.split(":", 1)
                d[k.strip()] = _parse_scalar(v)
        return d
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s in ("true", "false"):
        return s == "true"
    try:
        return int(s)
    except ValueError:
        return s


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        kv = re.match(r"^([A-Za-z0-9_]+)\s*:\s*(.*)$", line)
        if kv:
            meta[kv.group(1)] = _parse_scalar(kv.group(2))
    return meta, text[m.end():]


def dump_frontmatter(meta):
    lines = ["---"]
    for k, v in meta.items():
        if v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            items = ", ".join(json.dumps(i, ensure_ascii=False) if isinstance(i, dict) else
                              (f'"{i}"' if isinstance(i, str) and (" " in i or ":" in i) else str(i))
                              for i in v)
            lines.append(f"{k}: [{items}]")
        else:
            v = str(v)
            if any(c in v for c in ":,[]#") or v.strip() != v or not v:
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------- YAML 子集解析器
# 支持：嵌套 mapping、块列表（缩进更深或与键同缩进）、"- key: val" 列表项映射（manifest 形态）、行内列表。

def parse_yaml(text):
    root = {}
    stack = [[-1, root, None, None, False]]  # [indent, container, owner, key, from_item]
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        is_item = stripped.startswith("- ") or stripped == "-"
        if is_item:
            while len(stack) > 1 and (indent < stack[-1][0]
                                      or (indent == stack[-1][0] and stack[-1][4])):
                top_ = stack[-1]
                if top_[2] is not None and (
                        isinstance(top_[1], list)
                        or (isinstance(top_[1], dict) and not top_[1])):
                    break  # 键占位（空 dict 或已转列表）接受更浅缩进的列表项（父级缩进风格）
                stack.pop()
        else:
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()
        top = stack[-1]
        parent = top[1]
        if is_item:
            item_text = stripped[1:].strip() if stripped != "-" else ""
            if isinstance(parent, dict) and not parent and top[2] is None and len(stack) == 1:
                new_list = []            # 文档顶层即块列表（manifest.yaml 形态）
                stack[0][1] = new_list
                parent = new_list
            m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.+)$", item_text) if item_text else None
            if m:
                child = {m.group(1): _parse_scalar(m.group(2))}
                if isinstance(parent, list):
                    parent.append(child)
                    stack.append([indent, child, None, None, True])
                elif top[2] is not None and isinstance(parent, dict) and not parent:
                    top[2][top[3]] = [child]   # 空 dict 占位 → 列表
                    top[1] = top[2][top[3]]
                    stack.append([indent, child, None, None, True])
            else:
                val = _parse_scalar(item_text) if item_text else None
                if isinstance(parent, list):
                    parent.append(val)
                elif top[2] is not None and isinstance(parent, dict) and not parent:
                    top[2][top[3]] = [val]
                    top[1] = top[2][top[3]]
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", stripped)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val:
            parent[key] = _parse_scalar(val)
        else:
            child = {}
            parent[key] = child
            stack.append([indent, child, parent, key, False])
    return stack[0][1]


# ---------------------------------------------------------- entry 模型与装载

class Entry:
    def __init__(self, rel_path, meta, body):
        self.path = rel_path
        self.meta = meta or {}
        self.body = body

    @property
    def rel(self):
        return self.path.as_posix()

    @property
    def kind(self):
        if self.path.suffix == ".yaml":
            return "registry"
        return str(self.meta.get("kind") or "")

    @property
    def maturity(self):
        return str(self.meta.get("maturity") or "draft")

    @property
    def title(self):
        return str(self.meta.get("title") or self.meta.get("display_name")
                   or self.meta.get("name") or self.path.stem)

    @property
    def tags(self):
        t = self.meta.get("tags")
        return [str(x) for x in t] if isinstance(t, list) else []

    @property
    def risk(self):
        return self.meta.get("risk")

    @property
    def automation(self):
        return str(self.meta.get("automation") or "")

    def line(self):
        segs = [f"**[{self.title}]({self.rel})**", self.kind, self.maturity]
        if self.risk:
            segs.append(f"risk:{self.risk}")
        if self.automation:
            segs.append(self.automation)
        if self.tags:
            segs.append(" ".join("#" + t for t in self.tags))
        return "- " + " · ".join(segs)

    def anchor_clock(self, ref_index):
        cand = []
        if ref_index and self.rel in ref_index:
            cand.append(ref_index[self.rel]["last_date"])
        for k in ("last_reviewed", "last_verified", "created"):
            d = parse_date(self.meta.get(k))
            if d:
                cand.append(d)
        return max(cand) if cand else None

    def save(self):
        self.path_abs.write_text(dump_frontmatter(self.meta) + "\n" + self.body,
                                 encoding="utf-8")

    @property
    def path_abs(self):
        return ROOT / self.path


def knowledge_dir(cfg):
    return ROOT / cfg["paths"]["knowledge"]


def load_md(cfg):
    entries = []
    d = knowledge_dir(cfg)
    if not d.is_dir():
        return entries
    for f in sorted(d.rglob("*.md")):
        if f.name in SKIP_FILES:
            continue
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        if meta is None:
            continue  # 缺 frontmatter 由 lint 报告
        entries.append(Entry(f.relative_to(ROOT), meta, body))
    return entries


def load_registry(cfg):
    """inventory*.yaml → 每资源一个伪条目（检索/索引可见）"""
    entries = []
    d = knowledge_dir(cfg)
    if not d.is_dir():
        return entries
    for f in sorted(d.rglob("inventory*.yaml")):
        if f.name in SKIP_FILES:
            continue
        data = parse_yaml(f.read_text(encoding="utf-8"))
        resources = data.get("resources") if isinstance(data, dict) else None
        rel = f.relative_to(ROOT)
        if isinstance(resources, list) and resources:
            for r in resources:
                if isinstance(r, dict):
                    entries.append(Entry(rel, r, ""))
        else:
            entries.append(Entry(rel, data if isinstance(data, dict) else {}, ""))
    return entries


def load_all(cfg):
    return load_md(cfg) + load_registry(cfg)


def domain_of(cfg, rel_path):
    """返回 (域键, 域路径) 或 (None, None)"""
    parts = rel_path.parts
    if len(parts) >= 2 and parts[0] == cfg["paths"]["knowledge"]:
        prefix = "/".join(parts[:2])
        for key, dmeta in cfg["domains"].items():
            if dmeta["path"] == prefix:
                return key, prefix
    return None, None


def expected_kinds_for(cfg, rel_path):
    """kind↔位置规则：返回该位置允许的 kind 集合；None=不校验；空集=该位置不放知识文件"""
    parts = rel_path.parts
    if len(parts) < 3 or parts[0] != cfg["paths"]["knowledge"]:
        return None
    name = parts[-1]
    if len(parts) == 3:  # 域顶层
        if name.endswith(".yaml"):
            return {"registry"} if name.startswith("inventory") else set()
        if name.startswith("faq"):
            return {"faq"}
        if name.startswith("architecture"):
            return {"architecture"}
        return {"runbook", "reference"}
    parent = parts[-2]
    if parent == "问题定位":
        return {"playbook"}
    if parent == "复盘":
        return {"case"}
    if parent == "方案设计":
        return {"adr"}
    if name.endswith(".yaml"):
        return set()
    return {"runbook", "reference"}


# ---------------------------------------------------------- manifest（脚本注册表）

def load_manifest(cfg):
    p = ROOT / cfg["paths"]["manifest"]
    if not p.exists():
        return []
    data = parse_yaml(p.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


# ---------------------------------------------------------- 引用旁车

def infra_dir():
    return ROOT / ".infra"


def refs_log_file():
    return infra_dir() / f"refs-{date.today().year}.jsonl"


def load_reference_index():
    index = {}
    d = infra_dir()
    if not d.is_dir():
        return index
    for path in sorted(d.glob("refs-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            rel = rec.get("ref")
            dte = parse_date(rec.get("date"))
            if not rel or not dte:
                continue
            if rel not in index:
                index[rel] = {"count": 0, "last_date": dte}
            index[rel]["count"] += 1
            if dte > index[rel]["last_date"]:
                index[rel]["last_date"] = dte
    return index


def append_reference(rel, context, actor=None):
    infra_dir().mkdir(parents=True, exist_ok=True)
    record = {"date": today_str(), "ref": rel, "context": context,
              "actor": actor or os_user()}
    with open(refs_log_file(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_log(event, actor, detail):
    infra_dir().mkdir(parents=True, exist_ok=True)
    path = infra_dir() / f"log-{date.today().year}.md"
    if not path.exists():
        path.write_text(f"# Infra 操作日志 {date.today().year}（append-only）\n\n",
                        encoding="utf-8")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"- [{today_str()}] {event} | {actor} | {detail}\n")


# ---------------------------------------------------------- 检索（加权评分）

def _norm_text(s):
    return unicodedata.normalize("NFKC", str(s)).lower()


def _tokens(s):
    s = _norm_text(s)
    words = set(re.findall(r"[a-z0-9]+", s))
    cjk = "".join(c for c in s if "\u4e00" <= c <= "\u9fff")
    bigrams = {cjk[i:i + 2] for i in range(len(cjk) - 1)} if len(cjk) > 1 else set()
    return words | set(cjk) | bigrams


def _h2_headings(body):
    return " ".join(m.group(1) for m in re.finditer(r"^##\s+(.+)$", body, re.M))


def score_entry(entry, terms):
    title_toks = _tokens(entry.title)
    tag_toks = _tokens(" ".join(entry.tags) + " " + entry.path.stem)
    h2_toks = _tokens(_h2_headings(entry.body))
    body_toks = _tokens(entry.body + " " + json.dumps(entry.meta, ensure_ascii=False))
    score = 0
    for t in terms:
        if t in title_toks:
            score += 4
        if t in tag_toks:
            score += 3
        if t in h2_toks:
            score += 2
        if t in body_toks:
            score += 1
    return score


KIND_BUDGET = {"playbook": "troubleshoot", "runbook": "ops_execute", "registry": "locate"}


def cmd_search(cfg, args):
    entries = load_all(cfg)
    if args.kind:
        wanted = args.kind if args.kind in KINDS else args.kind.rstrip("s")
        if wanted not in KINDS:
            die(f"未知 kind: {args.kind}（可选 {'/'.join(KINDS)}）")
        entries = [e for e in entries if e.kind == wanted]
        args.kind = wanted
    terms = _tokens(" ".join(args.query))
    scored = sorted(((score_entry(e, terms), e) for e in entries),
                    key=lambda p: (-p[0], p[1].rel))
    hits = [(s, e) for s, e in scored if s > 0][: args.limit]
    if not hits:
        out("[infra] 无匹配。可放宽关键词、去掉 --kind，或读 INDEX.md / 问题定位索引.md。")
        return
    out(f"[infra] 命中 {len(hits)} 条:")
    for s, e in hits:
        out(f"  {e.line()}")
    if args.full:
        for s, e in hits[: args.full]:
            out("\n" + "=" * 60)
            out(f"# {e.title}  ({e.rel})")
            if e.path.suffix == ".yaml":
                out(e.path_abs.read_text(encoding="utf-8").strip())
            else:
                out((dump_frontmatter(e.meta) + "\n" + e.body).strip())
    else:
        bkey = KIND_BUDGET.get(args.kind or "", "default")
        b = cfg["budgets"].get(bkey, {})
        out(f"\n  预算[{bkey}]: {b.get('hint', '')}（目录≤{b.get('dirs', 2)}，全文≤{b.get('full', 5)}）")


# ---------------------------------------------------------- 三级索引 + 路由三件套

def cmd_index(cfg, args):
    entries = load_all(cfg)
    levels = cfg["maturity"]["levels"]
    auto_levels = cfg["automation_levels"]

    # 域 INDEX.md（二级索引）
    by_domain = {}
    for e in entries:
        _, prefix = domain_of(cfg, e.path)
        if prefix:
            by_domain.setdefault(prefix, []).append(e)
    kd = knowledge_dir(cfg)
    for prefix, es in sorted(by_domain.items()):
        lines = [
            f"# {Path(prefix).name} — 域索引",
            "",
            f"> 自动生成，勿手改；共 {len(es)} 条。刷新: `python scripts/infra.py index`",
            "",
        ]
        lines += [e.line() for e in sorted(es, key=lambda x: x.rel)]
        lines.append("")
        (ROOT / prefix / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    if kd.is_dir():
        for idx in kd.rglob("INDEX.md"):
            if "/".join(idx.relative_to(ROOT).parts[:2]) not in by_domain:
                idx.unlink()

    # 根 INDEX.md（一级索引 + 自动化仪表盘）
    total = len(entries)
    a = [
        "# 基础设施知识库 · 总索引",
        "",
        f"> 自动生成于 {today_str()}，共 {total} 条。三级检索：本文件 → 域 INDEX.md → 按预算读全文。",
        "> 排障先读 [问题定位索引.md](问题定位索引.md)；执行脚本先查 scripts/manifest.yaml（三层闸门见 AGENTS.md）。",
        "",
        "| 域 | 路径 | 条数 | " + "/".join(auto_levels) + " | " + "/".join(levels) + " |",
        "|---|---|---|---|---|",
    ]
    for key, dmeta in cfg["domains"].items():
        prefix = dmeta["path"]
        es = by_domain.get(prefix, [])
        ac = "/".join(str(sum(1 for e in es if e.automation == lv)) for lv in auto_levels)
        mc = "/".join(str(sum(1 for e in es if e.maturity == lv)) for lv in levels)
        a.append(f"| {dmeta['title']} | [{prefix}/]({prefix}/INDEX.md) | {len(es)} | {ac} | {mc} |")
    a += ["", "## 按任务类型的查询预算", ""]
    for task, b in cfg["budgets"].items():
        a.append(f"- **{task}**: {b.get('hint', '')}（目录≤{b.get('dirs', 2)}，全文≤{b.get('full', 5)}）")
    a.append("")
    (ROOT / "INDEX.md").write_text("\n".join(a), encoding="utf-8")

    # 问题定位索引.md（症状路由：数据来自 playbook frontmatter）
    manifest = {m.get("path"): m.get("name") for m in load_manifest(cfg)
                if isinstance(m, dict)}
    rows = []
    for e in entries:
        if e.kind != "playbook":
            continue
        sym = e.meta.get("symptoms")
        if not (isinstance(sym, list) and sym):
            continue
        script = str(e.meta.get("script") or "—")
        script = manifest.get(script, script)
        skill = str(e.meta.get("skill") or "—")
        rows.append((e, sym, script, skill))
    s = [
        "# 问题定位索引（自动生成）",
        "",
        "> 症状 → 域 → 文档 → 脚本 → skill。由 playbook frontmatter 的 symptoms/script/skill 生成，勿手改。",
        "",
        "| 症状 | 域 | 详细文档 | 脚本 | skill |",
        "|---|---|---|---|---|",
    ]
    for e, sym, script, skill in sorted(rows, key=lambda r: r[0].rel):
        dkey, _ = domain_of(cfg, e.path)
        s.append(f"| {'、'.join(str(x) for x in sym)} | {dkey or '?'} | [{e.title}]({e.rel}) "
                 f"| {script} | {skill} |")
    s.append("")
    (ROOT / cfg["paths"]["symptom_index"]).write_text("\n".join(s), encoding="utf-8")

    # 域路由表.yaml（agent 寻址入口）
    r = ["# 自动生成（infra.py index），勿手改。agent 寻址优先查本表。",
         "domains:"]
    for key, dmeta in cfg["domains"].items():
        r.append(f"  {key}: {dmeta['path']}")
    (ROOT / cfg["paths"]["domain_routes"]).write_text("\n".join(r) + "\n",
                                                      encoding="utf-8")
    out(f"[infra] 索引已刷新: {len(by_domain)} 个域, {total} 条 → "
        f"INDEX.md / {cfg['paths']['symptom_index']} / {cfg['paths']['domain_routes']}")
    append_log("index", os_user(), f"{total} entries")


# ---------------------------------------------------------- lint

def cmd_lint(cfg, args):
    lcfg = cfg["lint"]
    levels = set(cfg["maturity"]["levels"])
    auto_levels = set(cfg["automation_levels"])
    issues, warnings = [], []
    n_md = 0

    manifest = load_manifest(cfg)
    mpath = ROOT / cfg["paths"]["manifest"]
    if not mpath.exists():
        issues.append(f"{cfg['paths']['manifest']}: 脚本注册表缺失")
        manifest = []
    manifest_paths, manifest_names = set(), set()
    for i, m in enumerate(manifest):
        if not isinstance(m, dict):
            issues.append(f"manifest[{i}]: 条目必须是映射")
            continue
        name = m.get("name") or f"manifest[{i}]"
        for key in ("name", "path", "domain", "risk_level", "entry_command", "related_doc"):
            if not m.get(key):
                issues.append(f"manifest {name}: 缺少 {key}")
        if m.get("domain") and m["domain"] not in cfg["domains"]:
            issues.append(f"manifest {name}: 未知 domain {m['domain']}")
        if m.get("risk_level") and m["risk_level"] not in lcfg["manifest_risk_levels"]:
            issues.append(f"manifest {name}: risk_level 非法（{'/'.join(lcfg['manifest_risk_levels'])}）")
        p = m.get("path")
        if p:
            if not (ROOT / str(p)).exists():
                issues.append(f"manifest {name}: path 不存在 {p}")
            if str(p) in manifest_paths:
                issues.append(f"manifest {name}: path 重复登记 {p}")
            if m.get("name") in manifest_names:
                issues.append(f"manifest {name}: name 重复")
            manifest_paths.add(str(p))
            manifest_names.add(m.get("name"))
            if m.get("risk_level") == "change":
                content = ""
                sp = ROOT / str(p)
                if sp.exists():
                    content = sp.read_text(encoding="utf-8", errors="replace")
                if "dry-run" not in content and "dry_run" not in content:
                    issues.append(f"manifest {name}: change 类脚本必须支持 --dry-run")
        rd = m.get("related_doc")
        if rd and not (ROOT / str(rd)).exists():
            issues.append(f"manifest {name}: related_doc 不存在 {rd}")

    kd = knowledge_dir(cfg)
    for f in (sorted(kd.rglob("*.md")) if kd.is_dir() else []):
        if f.name in SKIP_FILES:
            continue
        rel = f.relative_to(ROOT).as_posix()
        n_md += 1
        meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
        if meta is None:
            issues.append(f"{rel}: 缺少 frontmatter（用 `python scripts/infra.py new` 生成骨架）")
            continue
        e = Entry(f.relative_to(ROOT), meta, body)
        for key in ("title", "owner", "kind", "maturity"):
            if key not in meta:
                issues.append(f"{rel}: frontmatter 缺少 {key}")
        if meta.get("kind") not in KINDS:
            issues.append(f"{rel}: kind 非法（可选 {'/'.join(KINDS)}）")
            continue
        if e.maturity not in levels:
            issues.append(f"{rel}: maturity 非法（可选 {'/'.join(sorted(levels))}）")
        if not str(meta.get("title") or "").strip():
            issues.append(f"{rel}: title 为空")
        if not str(meta.get("owner") or "").strip():
            warnings.append(f"{rel}: owner 为空（转正前必须补）")
        if not parse_date(meta.get("created")):
            issues.append(f"{rel}: created 缺失或格式错误（YYYY-MM-DD）")
        # kind ↔ 位置
        expected = expected_kinds_for(cfg, e.path)
        if expected is not None:
            if not expected:
                issues.append(f"{rel}: 该位置不存放知识文件（inventory 只放域顶层）")
            elif e.kind not in expected:
                issues.append(f"{rel}: kind={e.kind} 与位置不符（此处允许 {'/'.join(sorted(expected))}）")
        # risk / automation
        if e.kind in lcfg["risk_kinds"] and e.risk not in ("low", "medium", "high"):
            issues.append(f"{rel}: {e.kind} 必须声明 risk(low/medium/high)")
        if e.kind in lcfg["automation_kinds"]:
            if e.automation and e.automation not in auto_levels:
                issues.append(f"{rel}: automation 非法（{'/'.join(sorted(auto_levels))}）")
            if e.kind == "playbook" and not (isinstance(meta.get("symptoms"), list)
                                             and meta.get("symptoms")):
                warnings.append(f"{rel}: playbook 建议标 symptoms（进问题定位索引）")
        # 脚本/技能接线
        script = meta.get("script")
        if script:
            if not (ROOT / str(script)).exists():
                issues.append(f"{rel}: script 不存在 {script}")
            elif str(script) not in manifest_paths:
                issues.append(f"{rel}: script 未在 manifest 登记 {script}")
        skill = meta.get("skill")
        if skill and not (ROOT / cfg["paths"]["skills"] / str(skill) / "SKILL.md").exists():
            issues.append(f"{rel}: skill 不存在 {skill}")
        # related
        rel_list = meta.get("related")
        if rel_list is not None and not isinstance(rel_list, list):
            issues.append(f"{rel}: related 应为列表")
        else:
            for r in (rel_list or []):
                if not (ROOT / str(r)).exists():
                    issues.append(f"{rel}: related 指向不存在的 {r}")
        # 模板章节
        sec_key = f"{e.kind}_requires"
        if sec_key in lcfg:
            for sec in lcfg[sec_key]:
                if sec not in body:
                    issues.append(f"{rel}: {e.kind} 缺少「{sec}」章节")

    # inventory.yaml
    today = date.today()
    if kd.is_dir():
        for f in sorted(kd.rglob("inventory*.yaml")):
            rel = f.relative_to(ROOT).as_posix()
            data = parse_yaml(f.read_text(encoding="utf-8"))
            resources = data.get("resources") if isinstance(data, dict) else None
            if not isinstance(resources, list):
                issues.append(f"{rel}: 缺少 resources 列表")
                continue
            for i, r_ in enumerate(resources):
                if not isinstance(r_, dict):
                    issues.append(f"{rel}[{i}]: 资源必须是映射")
                    continue
                rn = r_.get("name") or f"[{i}]"
                for key in lcfg["registry_required"]:
                    if key not in r_ or r_.get(key) in (None, "", {}, []):
                        issues.append(f"{rel} {rn}: 缺少必填字段 {key}")
                lr = parse_date(r_.get("last_reviewed"))
                if not lr:
                    warnings.append(f"{rel} {rn}: last_reviewed 缺失")
                elif (today - lr).days > lcfg["registry_review_days"]:
                    warnings.append(f"{rel} {rn}: last_reviewed 已 "
                                    f"{months_between(lr, today)} 个月未复审"
                                    f"（阈值 {lcfg['registry_review_days']} 天）")
                kn = r_.get("knowledge")
                if isinstance(kn, dict):
                    for group, links in kn.items():
                        for lk in (links if isinstance(links, list) else []):
                            if not (ROOT / str(lk)).exists():
                                issues.append(f"{rel} {rn}: knowledge.{group} 指向不存在的 {lk}")

    out(f"[infra] lint 完成: {n_md} 个 md + {len(manifest)} 个登记脚本 | "
        f"错误 {len(issues)} | 警告 {len(warnings)}")
    for i in issues:
        out(f"  [E] {i}")
    for w in warnings:
        out(f"  [W] {w}")
    if issues:
        sys.exit(1)


# ---------------------------------------------------------- 衰减（只降级+建议）

def cmd_decay(cfg, args):
    dcfg = cfg["decay"]
    ref_index = load_reference_index()
    today = date.today()
    actions = []
    for e in load_md(cfg):
        if e.kind not in ("runbook", "playbook"):
            continue  # 台账走 last_reviewed 告警；faq/adr/case/architecture/reference 豁免
        clock = e.anchor_clock(ref_index)
        if not clock:
            continue
        months = months_between(clock, today)
        if e.maturity == "proven" and months >= dcfg["proven_months"]:
            e.meta["maturity"] = "verified"
            actions.append(f"{e.rel}: proven→verified（{months} 月无引用/复审信号）")
            e.save()
        elif e.maturity == "verified" and months >= dcfg["demote_verified_months"]:
            e.meta["maturity"] = "draft"
            actions.append(f"{e.rel}: verified→draft（{months} 月无引用/复审信号）")
            e.save()
        elif (e.maturity == "draft" and months >= dcfg["demote_verified_months"]
              and ref_index.get(e.rel, {}).get("count", 0) == 0):
            actions.append(f"[建议删除] {e.rel}: draft 且 {months} 月无引用"
                           f"（git rm 后提交，git 历史可恢复）")
    if not actions:
        out("[infra] decay: 无需衰减的条目")
    else:
        out(f"[infra] decay: {len(actions)} 项")
        for a_ in actions:
            out(f"  {a_}")
    append_log("decay", os_user(), f"{len(actions)} actions")


# ---------------------------------------------------------- reference / verify / new

def _resolve_entry(rel_or_path):
    p = Path(rel_or_path)
    p = p if p.is_absolute() else ROOT / p
    if not p.exists():
        return None
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None


def cmd_reference(cfg, args):
    ref_index = load_reference_index()
    for raw in args.paths:
        rel = _resolve_entry(raw)
        if not rel:
            out(f"[infra] 未找到 {raw}（路径相对仓库根，如 knowledge/06-存储/问题定位/xxx.md）")
            continue
        append_reference(rel, args.in_context)
        cnt = ref_index.get(rel, {}).get("count", 0) + 1
        out(f"[infra] 已记引用: {rel}（累计 {cnt} 次，上下文: {args.in_context}）")
    append_log("reference", os_user(), " ".join(args.paths))


def cmd_verify(cfg, args):
    rel = _resolve_entry(args.path)
    if not rel:
        die(f"未找到 {args.path}")
    p = ROOT / rel
    if p.suffix == ".yaml":
        text = p.read_text(encoding="utf-8")
        n = len(re.findall(r"(?m)^(\s*)last_reviewed:.*$", text))
        text = re.sub(r"(?m)^(\s*)last_reviewed:.*$", r"\1last_reviewed: " + today_str(), text)
        p.write_text(text, encoding="utf-8")
        out(f"[infra] inventory 复审已记录: {rel}（{n} 条资源 last_reviewed={today_str()}）")
    else:
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        if meta is None:
            die(f"{rel} 缺少 frontmatter")
        if args.proven:
            meta["maturity"] = "proven"
        else:
            if meta.get("maturity") == "proven":
                die("已是 proven；降级请手改 frontmatter")
            meta["maturity"] = "verified"
        meta["last_verified"] = today_str()
        p.write_text(dump_frontmatter(meta) + "\n" + body, encoding="utf-8")
        out(f"[infra] 已验证: {rel} → {meta['maturity']}（last_verified={today_str()}）")
    append_log("verify", os_user(), rel)


def cmd_new(cfg, args):
    if args.kind not in KINDS:
        die(f"未知 kind: {args.kind}（可选 {'/'.join(KINDS)}）")
    dmeta = cfg["domains"].get(args.domain)
    if not dmeta:
        die(f"未知 domain: {args.domain}（可选 {'/'.join(cfg['domains'])}；见 域路由表.yaml）")
    top = dmeta["path"]
    slug = args.slug
    if args.kind == "registry":
        dest = ROOT / top / "inventory.yaml"
        if dest.exists():
            die(f"已存在 {dest.relative_to(ROOT).as_posix()}（台账每域一份，直接编辑追加资源）")
    elif args.kind == "playbook":
        dest = ROOT / top / "问题定位" / f"{slug}.md"
    elif args.kind == "case":
        dest = ROOT / top / "复盘" / f"{slug}.md"
    elif args.kind == "adr":
        existing = [p.name.split("-")[0] for p in (ROOT / top / "方案设计").glob("*.md")
                    if p.name[:4].isdigit()]
        num = max([int(x) for x in existing if x.isdigit()] or [0]) + 1
        dest = ROOT / top / "方案设计" / f"{num:04d}-{slug}.md"
    else:
        if args.kind == "faq" and not slug.startswith("faq"):
            slug = f"faq-{slug}"
        if args.kind == "architecture" and not slug.startswith("architecture"):
            slug = f"architecture-{slug}"
        dest = ROOT / top / f"{slug}.md"
    if dest.exists():
        die(f"已存在 {dest.relative_to(ROOT).as_posix()}")
    tpl = ROOT / "templates" / KIND_TEMPLATES[args.kind]
    if not tpl.exists():
        die(f"缺少模板 {tpl.as_posix()}")
    text = tpl.read_text(encoding="utf-8")
    if args.kind == "registry":
        text = re.sub(r"(?m)^last_reviewed:.*$", f"last_reviewed: {today_str()}", text)
    else:
        meta, body = parse_frontmatter(text)
        meta["title"] = args.title or slug
        meta["owner"] = os_user()
        meta["created"] = today_str()
        if args.tags:
            meta["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
        if args.kind in ("runbook", "playbook") and "automation" not in meta:
            meta["automation"] = "L0"
        text = dump_frontmatter(meta) + "\n" + body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    out(f"[infra] 已生成: {dest.relative_to(ROOT).as_posix()}（maturity=draft）"
        f"——补内容后跑 lint，git diff/commit 即评审")
    append_log("new", os_user(), dest.relative_to(ROOT).as_posix())


# ---------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(prog="infra.py", description="基础设施知识库引擎（方案D域制）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="生成索引三件套（INDEX/问题定位索引/域路由表）")

    p_s = sub.add_parser("search", help="加权检索")
    p_s.add_argument("query", nargs="+")
    p_s.add_argument("--kind", help="registry/runbook/playbook/adr/faq/architecture/case/reference")
    p_s.add_argument("--limit", type=int, default=5)
    p_s.add_argument("--full", type=int, default=0, help="输出前 N 条全文")

    sub.add_parser("lint", help="结构/链接/manifest 治理")

    sub.add_parser("decay", help="成熟度衰减（只降级+删除建议）")

    p_r = sub.add_parser("reference", help="记录引用（写侧车日志）")
    p_r.add_argument("paths", nargs="+")
    p_r.add_argument("--in", dest="in_context", default="manual", metavar="CTX")

    p_v = sub.add_parser("verify", help="验证/复审条目")
    p_v.add_argument("path")
    p_v.add_argument("--proven", action="store_true", help="标记为 proven（实战检验）")

    p_n = sub.add_parser("new", help="按模板生成到目标域")
    p_n.add_argument("kind", choices=list(KINDS))
    p_n.add_argument("slug", help="文件名（中文，产品名保留英文）")
    p_n.add_argument("--domain", required=True, help="域键，见 域路由表.yaml")
    p_n.add_argument("--title", help="中文标题")
    p_n.add_argument("--tags", help="逗号分隔")

    args = ap.parse_args(argv)
    cfg = load_config()
    {"index": cmd_index, "search": cmd_search, "lint": cmd_lint,
     "decay": cmd_decay, "reference": cmd_reference, "verify": cmd_verify,
     "new": cmd_new}[args.cmd](cfg, args)


if __name__ == "__main__":
    main()
