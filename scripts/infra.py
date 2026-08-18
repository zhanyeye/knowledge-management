#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""infra.py — 基础设施知识库引擎（纯标准库，零依赖）

子命令：
  index               生成 INDEX.md（根）+ 各目录 INDEX.md（三级索引）
  search <词...>      加权检索（标题x4 tagsx3 H2x2 正文x1），--kind 过滤
  lint                结构/链接/时效治理，错误时退出码 1
  decay               成熟度衰减（verified 6月无信号降 draft；draft 归档建议需 --fix）
  reference <路径...> 记引用（写 .infra/refs-YYYY.jsonl，不改条目）
  verify <路径>       升成熟度 / registry 复审（写 last_reviewed）
  new <kind> <slug>   按模板生成骨架到 草稿箱/

约定见 AGENTS.md；配置在 scripts/infra.json。
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

KINDS = ("registry", "runbook", "playbook", "adr", "faq", "architecture", "case")
KIND_DIRS = {
    "registry": "台账",
    "runbook": "手册",
    "playbook": "排障",
    "adr": "决策",
    "faq": "问答",
    "architecture": "架构",
    "case": "案例",
}
KIND_DESC = {
    "registry": "资产台账：对象事实卡（在哪/谁负责/入口）",
    "runbook": "操作手册：这件事怎么做、怎么回滚",
    "playbook": "排障手册：这个症状怎么查",
    "adr": "决策记录：为什么这样设计",
    "faq": "高频问答：1 分钟短答案",
    "architecture": "架构说明：链路/拓扑/数据流",
    "case": "故障复盘：真实案例怎么定位的",
}
SKIP_FILES = {"INDEX.md", "MANIFEST.md", "README.md"}


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


# ---------------------------------------------------------- registry YAML（子集解析器）
# 支持：嵌套 mapping、块列表（缩进更深或与键同缩进）、行内列表、标量。足够台账 schema 使用。

def parse_yaml(text):
    root = {}
    stack = [[-1, root, None, None]]  # [indent, container, owner_dict, owner_key]
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        is_item = stripped.startswith("- ") or stripped == "-"
        while len(stack) > 1 and (indent < stack[-1][0]
                                  or (indent == stack[-1][0] and not is_item)):
            stack.pop()
        top = stack[-1]
        parent = top[1]
        if is_item:
            val = _parse_scalar(stripped[1:].strip()) if stripped != "-" else None
            if isinstance(parent, list):
                parent.append(val)
            elif top[2] is not None and not parent:  # 空 dict 占位 → 转为 list
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
            stack.append([indent, child, parent, key])
    return root


# ---------------------------------------------------------- entry 模型

class Entry:
    def __init__(self, rel_path, meta, body):
        self.path = rel_path          # 相对 ROOT 的 Path
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

    def line(self):
        risk_s = f" · risk:{self.risk}" if self.risk else ""
        tag_s = (" · " + " ".join("#" + t for t in self.tags)) if self.tags else ""
        return f"- **[{self.title}]({self.rel})** · {self.kind} · {self.maturity}{risk_s}{tag_s}"

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


def scan_top_dirs():
    return [d for d in KIND_DIRS.values()] + ["草稿箱"]


def load_md(include_inbox=True):
    entries = []
    tops = list(KIND_DIRS.values()) + (["草稿箱"] if include_inbox else [])
    for top in tops:
        d = ROOT / top
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.md")):
            if f.name in SKIP_FILES:
                continue
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            if meta is None:
                continue  # 缺 frontmatter 由 lint 报告
            entries.append(Entry(f.relative_to(ROOT), meta, body))
    return entries


def load_registry():
    entries = []
    d = ROOT / "台账"
    if not d.is_dir():
        return entries
    for f in sorted(d.rglob("*.yaml")):
        if f.name in SKIP_FILES:
            continue
        data = parse_yaml(f.read_text(encoding="utf-8"))
        entries.append(Entry(f.relative_to(ROOT), data, ""))
    return entries


def load_all(include_inbox=True):
    return load_md(include_inbox) + load_registry()


# ---------------------------------------------------------- 引用旁车（.infra/refs-YYYY.jsonl）

def infra_dir():
    return ROOT / ".infra"


def refs_log_file():
    return infra_dir() / f"refs-{date.today().year}.jsonl"


def load_reference_index():
    """rel_path -> {count, last_date}，聚合全部 refs-*.jsonl"""
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
    entries = load_all()
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
        out("[infra] 无匹配。可放宽关键词、去掉 --kind 过滤，或读 INDEX.md 换分区。")
        return
    where = "（含草稿箱）" if any(e.path.parts[0] == "草稿箱" for _, e in hits) else ""
    out(f"[infra] 命中 {len(hits)} 条{where}:")
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


# ---------------------------------------------------------- 三级索引

def cmd_index(cfg, args):
    entries = load_all()
    by_dir = {}
    for e in entries:
        if e.path.parts[0] == "草稿箱":
            continue
        by_dir.setdefault(e.path.parent.as_posix(), []).append(e)

    # 各目录 INDEX.md（直接包含条目的目录）
    for d, es in sorted(by_dir.items()):
        lines = [
            f"# {Path(d).name}/ — 目录索引",
            "",
            f"> 自动生成，勿手改；共 {len(es)} 条。刷新: `python scripts/infra.py index`",
            "",
        ]
        lines += [e.line() for e in sorted(es, key=lambda x: x.rel)]
        lines.append("")
        (ROOT / d / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")

    # 清理无条目目录的过期索引
    for top in KIND_DIRS.values():
        d = ROOT / top
        if d.is_dir():
            for idx in d.rglob("INDEX.md"):
                if idx.parent.relative_to(ROOT).as_posix() not in by_dir:
                    idx.unlink()

    # 根 INDEX.md
    levels = cfg["maturity"]["levels"]
    a = [
        "# 基础设施知识库 · 总索引",
        "",
        f"> 自动生成于 {today_str()}，共 {len(entries)} 条。"
        "查询协议：本文件 → 目录 INDEX.md → 按预算读条目全文（预算见 scripts/infra.json）。",
        "",
        "| 分区 | 装什么 | 条数 | " + "/".join(levels) + " |",
        "|---|---|---|---|",
    ]
    for kind in KINDS:
        top = KIND_DIRS[kind]
        es = [e for e in entries if e.path.parts[0] == top]
        counts = "/".join(str(sum(1 for e in es if e.maturity == lv)) for lv in levels)
        a.append(f"| [{top}/]({top}/INDEX.md) | {KIND_DESC[kind]} | {len(es)} | {counts} |")

    inbox_es = [e for e in entries if e.path.parts[0] == "草稿箱"]
    if inbox_es:
        a += ["", "## 草稿箱（待人工确认的草稿）", ""]
        a += [e.line() for e in sorted(inbox_es, key=lambda x: x.rel)]
        a.append("")
        a.append("> 确认后 `git mv 草稿箱/<文件> <目标分区>/` 并重跑 `python scripts/infra.py index`。")

    a += ["", "## 按任务类型的查询预算", ""]
    for task, b in cfg["budgets"].items():
        a.append(f"- **{task}**: {b.get('hint', '')}（目录≤{b.get('dirs', 2)}，全文≤{b.get('full', 5)}）")
    a.append("")
    (ROOT / "INDEX.md").write_text("\n".join(a), encoding="utf-8")
    out(f"[infra] 索引已刷新: {len(by_dir)} 个目录, {len(entries)} 条 → INDEX.md")
    append_log("index", os_user(), f"{len(entries)} entries")


# ---------------------------------------------------------- lint

def _walk_md_files():
    for top in scan_top_dirs():
        d = ROOT / top
        if d.is_dir():
            for f in sorted(d.rglob("*.md")):
                if f.name not in SKIP_FILES:
                    yield f


def cmd_lint(cfg, args):
    lcfg = cfg["lint"]
    levels = set(cfg["maturity"]["levels"])
    issues, warnings = [], []
    all_md_rels = set()

    for f in _walk_md_files():
        rel = f.relative_to(ROOT).as_posix()
        all_md_rels.add(rel)
        text = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        top_dir = f.relative_to(ROOT).parts[0]
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
        # risk
        if e.kind in lcfg["kinds_requiring_risk"]:
            if e.risk not in ("low", "medium", "high"):
                issues.append(f"{rel}: {e.kind} 必须声明 risk(low/medium/high)")
        # kind 与目录匹配（草稿箱豁免：草稿区允许任何 kind）
        if top_dir != "草稿箱":
            expected = KIND_DIRS.get(e.kind)
            if expected and top_dir != expected:
                issues.append(f"{rel}: kind={e.kind} 应放在 {expected}/ 下")
        else:
            if e.maturity != "draft":
                warnings.append(f"{rel}: inbox 中应为 draft（转正时再升成熟度）")
        # related 链接存在性
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

    # registry YAML
    d = ROOT / "台账"
    if d.is_dir():
        today = date.today()
        for f in sorted(d.rglob("*.yaml")):
            if f.name in SKIP_FILES:
                continue
            rel = f.relative_to(ROOT).as_posix()
            data = parse_yaml(f.read_text(encoding="utf-8"))
            for key in lcfg["registry_required"]:
                if key not in data or data.get(key) in (None, "", {}, []):
                    issues.append(f"{rel}: registry 缺少必填字段 {key}")
            lr = parse_date(data.get("last_reviewed"))
            if not lr:
                warnings.append(f"{rel}: last_reviewed 缺失")
            elif (today - lr).days > lcfg["registry_review_days"]:
                warnings.append(f"{rel}: last_reviewed 已 {months_between(lr, today)} 个月未复审"
                                f"（阈值 {lcfg['registry_review_days']} 天）")
            kn = data.get("knowledge")
            if isinstance(kn, dict):
                for group, links in kn.items():
                    for lk in (links if isinstance(links, list) else []):
                        if not (ROOT / str(lk)).exists():
                            issues.append(f"{rel}: knowledge.{group} 指向不存在的 {lk}")

    out(f"[infra] lint 完成: {len(all_md_rels)} 个 md + registry | "
        f"错误 {len(issues)} | 警告 {len(warnings)}")
    for i in issues:
        out(f"  [E] {i}")
    for w in warnings:
        out(f"  [W] {w}")
    if issues:
        sys.exit(1)


# ---------------------------------------------------------- 衰减

def cmd_decay(cfg, args):
    dcfg = cfg["decay"]
    ref_index = load_reference_index()
    today = date.today()
    actions, archives = [], []
    for e in load_md(include_inbox=False):
        if e.kind not in ("runbook", "playbook"):
            continue  # registry 走 last_reviewed 告警；faq/adr/case/architecture 豁免
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
        elif (e.maturity == "draft" and months >= dcfg["archive_draft_months"]
              and ref_index.get(e.rel, {}).get("count", 0) == 0):
            archives.append(e)

    if args.fix and archives:
        for e in archives:
            arc = ROOT / "归档" / str(today.year)
            arc.mkdir(parents=True, exist_ok=True)
            (arc / e.path.name).write_text(
                dump_frontmatter(e.meta) + "\n" + e.body, encoding="utf-8")
            e.path_abs.unlink()
            actions.append(f"{e.rel}: 已归档 → archive/{today.year}/{e.path.name}")
    elif archives:
        for e in archives:
            actions.append(f"[建议] {e.rel}: draft 且 {dcfg['archive_draft_months']} 月无引用，"
                           f"可归档（decay --fix 执行）")

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
            out(f"[infra] 未找到 {raw}（路径相对仓库根，如 playbooks/disk-full.md）")
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
        text = re.sub(r"(?m)^last_reviewed:.*$", f"last_reviewed: {today_str()}", text)
        p.write_text(text, encoding="utf-8")
        out(f"[infra] registry 复审已记录: {rel}（last_reviewed={today_str()}）")
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
    ext = ".yaml" if args.kind == "registry" else ".md"
    dest = ROOT / "草稿箱" / (args.slug + ext)
    if dest.exists():
        die(f"已存在 {dest.relative_to(ROOT).as_posix()}")
    tpl = ROOT / "templates" / ("registry-resource.yaml" if args.kind == "registry"
                                else f"{args.kind}.md")
    if not tpl.exists():
        die(f"缺少模板 {tpl.as_posix()}")
    text = tpl.read_text(encoding="utf-8")
    if ext == ".yaml":
        text = re.sub(r"(?m)^name:.*$", f'name: {args.slug}', text)
        text = re.sub(r"(?m)^last_reviewed:.*$", f"last_reviewed: {today_str()}", text)
    else:
        meta, body = parse_frontmatter(text)
        meta["title"] = args.title or args.slug
        meta["owner"] = os_user()
        meta["created"] = today_str()
        if args.tags:
            meta["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
        text = dump_frontmatter(meta) + "\n" + body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    out(f"[infra] 已生成草稿: {dest.relative_to(ROOT).as_posix()}"
        f"（maturity=draft，人工确认后 git mv 到 {KIND_DIRS[args.kind]}/）")
    append_log("new", os_user(), dest.relative_to(ROOT).as_posix())


# ---------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(prog="infra.py", description="基础设施知识库引擎")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="生成三级索引")

    p_s = sub.add_parser("search", help="加权检索")
    p_s.add_argument("query", nargs="+")
    p_s.add_argument("--kind", help="registry/runbook/playbook/adr/faq/architecture/case")
    p_s.add_argument("--limit", type=int, default=5)
    p_s.add_argument("--full", type=int, default=0, help="输出前 N 条全文")

    sub.add_parser("lint", help="结构与链接治理")

    p_d = sub.add_parser("decay", help="成熟度衰减")
    p_d.add_argument("--fix", action="store_true", help="执行归档建议")

    p_r = sub.add_parser("reference", help="记录引用（写侧车日志）")
    p_r.add_argument("paths", nargs="+")
    p_r.add_argument("--in", dest="in_context", default="manual", metavar="CTX")

    p_v = sub.add_parser("verify", help="验证/复审条目")
    p_v.add_argument("path")
    p_v.add_argument("--proven", action="store_true", help="标记为 proven（实战检验）")

    p_n = sub.add_parser("new", help="按模板生成草稿到 inbox/")
    p_n.add_argument("kind", choices=list(KINDS))
    p_n.add_argument("slug", help="文件名，如 disk-full / mongo-pipelinex-prod")
    p_n.add_argument("--title", help="中文标题")
    p_n.add_argument("--tags", help="逗号分隔")

    args = ap.parse_args(argv)
    cfg = load_config()
    {"index": cmd_index, "search": cmd_search, "lint": cmd_lint,
     "decay": cmd_decay, "reference": cmd_reference, "verify": cmd_verify,
     "new": cmd_new}[args.cmd](cfg, args)


if __name__ == "__main__":
    main()
