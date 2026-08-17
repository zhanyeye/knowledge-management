#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队 wiki 引擎 (stdlib only)
用法：python .wiki/scripts/wiki.py <子命令>
  init      初始化目录/日志/索引
  index     重建索引（总目录 catalog.md + 各目录 catalog.md）
  search    预算受控检索
  new       新建条目（自动编号 + 模板）
  verify    记录一次人工验证（推动成熟度晋升）
  reference 记录一次引用（防衰减）
  promote   把 pending 候选/项目条目转正到目标分区
  decay     成熟度衰减与闲置归档
  lint      膨胀治理检查（schema/冲突/重复/闲置）
  stats     体检报告
  doctor    自检
  layer     分区管理：layer list | layer add <路径> --prefix XX --title 名 | layer rm <路径>
  type      类型管理：type list | type add <key> --title 名 | type rm <key>
"""
import argparse
import getpass
import json
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]   # .wiki/scripts/wiki.py → 仓库根
CONFIG_PATH = ROOT / ".wiki" / "config.json"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as ex:
        out(f"[wiki] 配置文件格式错误: {CONFIG_PATH.as_posix()}（第 {ex.lineno} 行第 {ex.colno} 列: {ex.msg}）")
        out("[wiki] 常见原因：多余/缺失逗号、引号未闭合、注释（JSON 不支持注释）。")
        out("[wiki] 修复后重试；改乱了可用 git checkout -- .wiki/config.json 恢复。")
        sys.exit(1)


def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def out(msg=""):
    print(msg)


def die(msg, code=1):
    out(f"[wiki] 错误: {msg}")
    sys.exit(code)


def today_str():
    return date.today().isoformat()


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def months_between(d1, d2):
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def log_dir(cfg):
    return ROOT / cfg["paths"]["log"]


def log_file(cfg):
    return log_dir(cfg) / f"log-{date.today().year}.md"


def append_log(cfg, event, actor, detail):
    log_dir(cfg).mkdir(parents=True, exist_ok=True)
    path = log_file(cfg)
    if not path.exists():
        path.write_text(f"# Wiki 操作日志 {date.today().year}（append-only）\n格式: [日期] 事件 | 操作者 | 详情\n\n",
                        encoding="utf-8")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{today_str()}] {event} | {actor} | {detail}\n")


def os_user():
    try:
        return getpass.getuser().lower()
    except Exception:
        return "unknown"


# 中文化与旧英文类型互通（lint / search --type 共用）
TYPE_ALIASES = {
    "规范": {"guideline"},
    "guideline": {"规范"},
    "手册": {"runbook"},
    "runbook": {"手册"},
}


def type_matches(entry_type, filter_type):
    if entry_type == filter_type:
        return True
    aliases = TYPE_ALIASES.get(filter_type, set())
    return entry_type in aliases


def is_guideline_type(entry_type):
    return entry_type in ("guideline", "规范")


def is_runbook_type(entry_type):
    return entry_type in ("runbook", "手册")


def refs_log_file(cfg, year=None):
    year = year or date.today().year
    return log_dir(cfg) / f"refs-{year}.jsonl"


def load_reference_index(cfg):
    """entry_id -> {count, last_date}，聚合全部 refs-*.jsonl"""
    index = {}
    d = log_dir(cfg)
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
            eid = rec.get("id")
            dte = parse_date(rec.get("date"))
            if not eid or not dte:
                continue
            if eid not in index:
                index[eid] = {"count": 0, "last_date": dte}
            index[eid]["count"] += 1
            if dte > index[eid]["last_date"]:
                index[eid]["last_date"] = dte
    return index


def reference_count(entry, ref_index):
    legacy = int(entry.meta.get("reference_count") or 0)
    sidecar = ref_index.get(entry.id, {}).get("count", 0) if ref_index else 0
    return legacy + sidecar


def entry_anchor_clock(entry, ref_index=None):
    if ref_index and entry.id in ref_index:
        return ref_index[entry.id]["last_date"]
    return parse_date(entry.meta.get("last_referenced")) \
        or parse_date(entry.meta.get("last_verified")) \
        or parse_date(entry.meta.get("created"))


def append_reference(cfg, entry_id, context, actor=None):
    log_dir(cfg).mkdir(parents=True, exist_ok=True)
    path = refs_log_file(cfg)
    record = {
        "date": today_str(),
        "id": entry_id,
        "context": context,
        "actor": actor or os_user(),
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------- frontmatter

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
        elif isinstance(v, dict):
            inner = ", ".join(f"{ik}: {iv}" for ik, iv in v.items())
            lines.append(f"{k}: {{{inner}}}")
        else:
            v = str(v)
            if any(c in v for c in ":,[]#") or v.strip() != v or not v:
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------- entries

class Entry:
    def __init__(self, path, meta, body, layer_root):
        self.path = path              # 相对 ROOT
        self.meta = meta or {}
        self.body = body
        self.dir_rel = path.parent.as_posix()
        self.layer_root = layer_root  # 所属注册分区（最具体的）

    @property
    def id(self):
        return self.meta.get("id", "?")

    @property
    def title(self):
        return self.meta.get("title", self.path.stem)

    @property
    def type(self):
        return self.meta.get("type", "?")

    @property
    def maturity(self):
        return self.meta.get("maturity", "draft")

    def line(self, cfg):
        type_title = cfg["types"].get(self.type, {}).get("title", self.type)
        risk = self.meta.get("risk")
        risk_s = f"|risk:{risk}" if risk else ""
        tags = self.meta.get("tags") or []
        tag_s = f" — {' '.join('#' + t for t in tags)}" if tags else ""
        return f"- **{self.id}** [{self.maturity}] ({type_title}{risk_s}) {self.title}{tag_s}"

    def anchor_clock(self, ref_index=None):
        return entry_anchor_clock(self, ref_index)


def registered_layers(cfg):
    """注册分区列表，按路径长度降序（最具体的在前）"""
    return sorted(((v["path"], v) for v in cfg["layers"].values() if v.get("active", True)),
                  key=lambda kv: len(kv[0]), reverse=True)


def layers_in_config_order(cfg):
    """注册分区列表，按 config.json 里的书写顺序（总目录/统计展示用）"""
    return [(v["path"], v) for v in cfg["layers"].values() if v.get("active", True)]


def owning_layer(cfg, dir_rel):
    for path_key, meta in registered_layers(cfg):
        if dir_rel == path_key or dir_rel.startswith(path_key + "/"):
            return path_key
    return None


def load_entries(cfg):
    entries = []
    for path_key in dict(registered_layers(cfg)):
        d = ROOT / path_key
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.md")):
            if f.name in ("catalog.md", "README.md"):
                continue
            rel_dir = f.parent.relative_to(ROOT).as_posix()
            if owning_layer(cfg, rel_dir) != path_key:
                continue  # 属于更具体的子分区
            meta, body = parse_frontmatter(f.read_text(encoding="utf-8"))
            if meta is None:
                continue
            entries.append(Entry(f.relative_to(ROOT), meta, body, path_key))
    return entries


def validations_of(entry):
    return [x for x in (entry.meta.get("validations") or []) if isinstance(x, dict)]


def save_entry(entry):
    entry.path.write_text(dump_frontmatter(entry.meta) + "\n" + entry.body, encoding="utf-8")


# ---------------------------------------------------------- index

def cmd_index(cfg, args):
    entries = load_entries(cfg)
    layer_meta = dict(layers_in_config_order(cfg))

    # 各目录索引（有条目的目录才生成）
    by_dir = {}
    for e in entries:
        by_dir.setdefault(e.dir_rel, []).append(e)
    for d, es in sorted(by_dir.items()):
        title = layer_meta.get(d, {}).get("title", Path(d).name)
        lines = [
            f"# {title} — 目录索引",
            "",
            f"> 自动生成，请勿手改；共 {len(es)} 条。刷新: `python .wiki/scripts/wiki.py index`",
            "",
        ]
        for e in sorted(es, key=lambda x: x.id):
            lines.append(e.line(cfg))
        lines.append("")
        (ROOT / d / "catalog.md").write_text("\n".join(lines), encoding="utf-8")

    # 清理已无条目目录的过期索引
    for path_key in dict(layer_meta):
        root_d = ROOT / path_key
        if root_d.is_dir():
            for c in root_d.rglob("catalog.md"):
                if c.parent.relative_to(ROOT).as_posix() not in by_dir:
                    c.unlink()

    # 总目录 catalog.md
    levels = cfg["maturity"]["levels"]
    a = [
        "# 团队 Wiki 总目录",
        "",
        f"> 自动生成于 {today_str()}，共 {len(entries)} 条。查询协议：本文件 → 目录 catalog.md → 按预算读条目全文。",
        "",
        "| 分区 | 目录 | 条数 | draft/verified/proven |",
        "|---|---|---|---|",
    ]
    for path_key, meta in layer_meta.items():  # 按配置注册顺序展示
        es = [e for e in entries if e.layer_root == path_key]
        counts = "/".join(str(sum(1 for e in es if e.maturity == lv)) for lv in levels)
        a.append(f"| {meta['title']} | {path_key}/ | {len(es)} | {counts} |")
    a += ["", "## 按任务类型的推荐查询路径", ""]
    for task, b in cfg["query_budgets"].items():
        a.append(f"- **{task}**: {b.get('hint', '')}（目录≤{b.get('layerB_dirs', 2)}，全文≤{b.get('full_entries', 5)}）")
    a += [
        "",
        "> 各项目私有知识在项目仓 `docs/wiki/`（接入包见 .wiki/templates/layer3-project/）。",
        "",
    ]
    (ROOT / cfg["paths"]["catalog"]).write_text("\n".join(a), encoding="utf-8")
    out(f"[wiki] 索引已刷新: {len(by_dir)} 个目录, {len(entries)} 条条目 → {cfg['paths']['catalog']}")


# ---------------------------------------------------------- search

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
    tag_toks = _tokens(" ".join(entry.meta.get("tags") or []) + " " + entry.id)
    h2_toks = _tokens(_h2_headings(entry.body))
    body_toks = _tokens(entry.body)
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


def cmd_search(cfg, args):
    entries = load_entries(cfg)
    if args.type:
        entries = [e for e in entries if type_matches(e.type, args.type)]
    if args.maturity:
        entries = [e for e in entries if e.maturity == args.maturity]
    if args.risk:
        entries = [e for e in entries if e.meta.get("risk") == args.risk]
    terms = _tokens(" ".join(args.query))
    scored = sorted(((score_entry(e, terms), e) for e in entries), key=lambda p: (-p[0], p[1].id))
    hits = [(s, e) for s, e in scored if s > 0][: args.limit]
    if not hits:
        out("[wiki] 无匹配。可放宽关键词，或读 catalog.md 换目录。")
        return
    out(f"[wiki] 命中 {len(hits)} 条（预算 limit={args.limit}，先读摘要再决定是否读全文）:")
    for s, e in hits:
        out(e.line(cfg) + f"  ← {e.path.as_posix()}")
    if args.full:
        for s, e in hits[: args.full]:
            out("\n" + "=" * 60)
            out(f"# {e.id} {e.title}")
            out((dump_frontmatter(e.meta) + "\n" + e.body).strip())
    if args.reference:
        _do_reference(cfg, [e.id for _, e in hits], args.reference)


# ---------------------------------------------------------- verify / reference

def find_entry(entries, entry_id):
    return next((e for e in entries if e.id == entry_id), None)


def _do_reference(cfg, ids, context):
    ref_index = load_reference_index(cfg)
    for entry_id in ids:
        entries = load_entries(cfg)
        e = find_entry(entries, entry_id)
        if not e:
            out(f"[wiki] 未找到 {entry_id}")
            continue
        append_reference(cfg, entry_id, context)
        ref_index = load_reference_index(cfg)
        total = reference_count(e, ref_index)
        out(f"[wiki] 已记录引用: {entry_id} (累计 {total} 次, 上下文: {context})")
        append_log(cfg, "reference", os_user(), f"{entry_id} context={context}")


def cmd_reference(cfg, args):
    _do_reference(cfg, args.ids, args.in_context or "manual")


def cmd_verify(cfg, args):
    entries = load_entries(cfg)
    e = find_entry(entries, args.id)
    if not e:
        die(f"未找到条目 {args.id}")
    vals = validations_of(e)
    vals.append({"by": args.by, "date": today_str(), "project": args.project or "-"})
    e.meta["validations"] = vals
    e.meta["last_verified"] = today_str()
    rule = cfg["maturity"]["promote"]
    promoted = None
    if e.maturity == "draft" and len(vals) >= rule["draft_to_verified"]["validations"]:
        e.meta["maturity"] = "verified"
        promoted = "draft→verified"
    elif e.maturity == "verified" and args.promote:
        people = {x["by"] for x in vals}
        projs = {x["project"] for x in vals if x["project"] != "-"}
        r2 = rule["verified_to_proven"]
        if len(people) >= r2["distinct_validators"] and len(projs) >= r2["distinct_projects"]:
            e.meta["maturity"] = "proven"
            promoted = "verified→proven"
        else:
            out(f"[wiki] 未达 proven 门槛: 需 ≥{r2['distinct_validators']} 人 × ≥{r2['distinct_projects']} 项目 "
                f"(当前 {len(people)} 人 {len(projs)} 项目)")
    save_entry(e)
    append_log(cfg, "verify", args.by,
               f"{args.id} by={args.by} project={args.project or '-'}"
               + (f" promoted={promoted}" if promoted else ""))
    out(f"[wiki] 已记录验证: {args.id}" + (f"，晋升 {promoted}" if promoted else ""))
    if promoted:
        cmd_index(cfg, args)


# ---------------------------------------------------------- decay

def cmd_decay(cfg, args):
    dcfg = cfg["maturity"]["decay"]
    today = date.today()
    actions = []
    ref_index = load_reference_index(cfg)
    for e in load_entries(cfg):
        if dcfg.get("evergreen_exempt") and e.meta.get("evergreen"):
            continue  # evergreen 条目豁免衰减（如核心红线/基础操作）
        clock = e.anchor_clock(ref_index)
        if not clock:
            continue
        months = months_between(clock, today)
        if e.maturity == "proven" and months >= dcfg["proven_months"]:
            e.meta["maturity"] = "verified"
            actions.append(f"{e.id} proven→verified (闲置 {months} 月)")
        elif e.maturity == "verified" and months >= dcfg["verified_months"]:
            e.meta["maturity"] = "draft"
            actions.append(f"{e.id} verified→draft (闲置 {months} 月)")
        elif (e.maturity == "draft" and months >= dcfg["archive_draft_months"]
              and not validations_of(e) and reference_count(e, ref_index) == 0):
            arc = ROOT / cfg["paths"]["archive"] / str(today.year)
            arc.mkdir(parents=True, exist_ok=True)
            new_path = arc / e.path.name
            e.path.rename(new_path)
            e.path = new_path.relative_to(ROOT)
            actions.append(f"{e.id} 归档 → {e.path.as_posix()} (draft 闲置 {months} 月, 零引用零验证)")
        else:
            continue
        save_entry(e)
    for a in actions:
        append_log(cfg, "decay", "system", a)
    if actions:
        cmd_index(cfg, args)
    out(f"[wiki] 衰减检查完成: {len(actions)} 项处理" + ("" if actions else "（全部健康）"))
    for a in actions:
        out("  - " + a)


# ---------------------------------------------------------- lint

def _title_jaccard(t1, t2):
    s1, s2 = _tokens(t1), _tokens(t2)
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def find_guideline_conflicts(entries, jaccard_threshold=0.3):
    """全库相反规范冲突：按 tag 聚类（跨分区），供 lint 与单测共用"""
    by_tag = {}
    for e in entries:
        if is_guideline_type(e.type):
            for t in set(e.meta.get("tags") or []):
                by_tag.setdefault(t, []).append(e)
    conflicts, seen_pairs = [], set()
    for tag, es in by_tag.items():
        for i in range(len(es)):
            for j in range(i + 1, len(es)):
                a, b = es[i], es[j]
                pair = tuple(sorted((a.id, b.id)))
                if pair in seen_pairs:
                    continue
                if a.meta.get("polarity") and b.meta.get("polarity") \
                        and a.meta["polarity"] != b.meta["polarity"] \
                        and _title_jaccard(a.title, b.title) >= jaccard_threshold:
                    seen_pairs.add(pair)
                    conflicts.append(f"{a.id}({a.meta['polarity']}) vs {b.id}({b.meta['polarity']}) — "
                                     f"{a.title} / {b.title}（#{tag}）")
    return conflicts


def cmd_lint(cfg, args):
    entries = load_entries(cfg)
    issues, warnings, autofixed = [], [], []
    types_cfg = cfg["types"]
    levels = set(cfg["maturity"]["levels"])
    layer_meta = dict(layers_in_config_order(cfg))
    all_ids = {e.id for e in entries}
    ref_index = load_reference_index(cfg)

    for e in entries:
        m = e.meta
        for field in ("id", "title", "type", "maturity", "owner", "created"):
            if not m.get(field):
                issues.append(f"{e.path}: 缺少必填字段 {field}")
        if m.get("type") and m["type"] not in types_cfg:
            issues.append(f"{e.id}: 未知类型 {m['type']}")
        if m.get("maturity") and m["maturity"] not in levels:
            issues.append(f"{e.id}: 未知成熟度 {m['maturity']}")
        prefix = layer_meta.get(e.layer_root, {}).get("prefix")
        if prefix and m.get("id") and m["id"].split("-")[0] != prefix:
            issues.append(f"{e.id}: 编号前缀应为 {prefix}（{e.layer_root} 分区）")
        for rid in m.get("related") or []:
            if rid not in all_ids:
                issues.append(f"{e.id}: related 指向不存在的 {rid}")
        if is_runbook_type(m.get("type")):
            if not m.get("risk"):
                issues.append(f"{e.id}: 手册类必须声明 risk(low/medium/high)")
            for sec in cfg["lint"]["runbook_requires"]:
                if sec not in e.body:
                    issues.append(f"{e.id}: 手册类缺少「{sec}」章节")
        if is_guideline_type(m.get("type")):
            if m.get("polarity") not in cfg["lint"]["guideline_polarity_values"]:
                issues.append(f"{e.id}: 规范类需 polarity: recommend|avoid")
            if "理由" not in e.body and "reason" not in e.body.lower():
                warnings.append(f"{e.id}: 规范类建议写明理由")
        clock = e.anchor_clock(ref_index)
        if clock and e.maturity == "draft":
            months = months_between(clock, date.today())
            if months >= cfg["maturity"]["decay"]["archive_draft_months"]:
                warnings.append(f"{e.id}: draft 闲置 {months} 月，运行 decay 归档或安排 /wiki-verify")

    seen = {}
    for e in entries:
        if e.id in seen:
            issues.append(f"重复编号: {e.id} ({seen[e.id]} 与 {e.path})")
        seen[e.id] = e.path

    conflicts = find_guideline_conflicts(entries)
    if conflicts:
        pdir = ROOT / cfg["paths"]["pending"]
        pdir.mkdir(parents=True, exist_ok=True)
        with open(pdir / "CONFLICTS.md", "a", encoding="utf-8") as f:
            f.write(f"\n## {today_str()} 自动检测\n")
            for c in conflicts:
                f.write(f"- {c}\n")
        issues.append(f"发现 {len(conflicts)} 对疑似冲突规范，已记录到 pending/CONFLICTS.md，请维护者仲裁")

    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            a, b = entries[i], entries[j]
            if a.dir_rel == b.dir_rel and _title_jaccard(a.title, b.title) >= cfg["lint"]["duplicate_title_jaccard"]:
                warnings.append(f"疑似重复: {a.id} 与 {b.id}（标题相似）→ 建议合并")

    if args.fix:
        cmd_index(cfg, args)
        autofixed.append("索引已重建")

    out(f"[wiki] lint 完成: {len(entries)} 条 | 错误 {len(issues)} | 警告 {len(warnings)} | 自动修复 {len(autofixed)}")
    for i in issues:
        out("  [ERROR] " + i)
    for w in warnings:
        out("  [WARN ] " + w)
    for f_ in autofixed:
        out("  [FIX  ] " + f_)
    if issues:
        sys.exit(1)


# ---------------------------------------------------------- new / promote

def next_id(cfg, layer_path):
    prefix = dict(registered_layers(cfg)).get(layer_path, {}).get("prefix", "W")
    nums = [int(m.group(1)) for e in load_entries(cfg) if e.layer_root == layer_path
            for m in [re.match(rf"^{prefix}-(\d+)$", e.id)] if m]
    return f"{prefix}-{max(nums, default=0) + 1:03d}"


def cmd_new(cfg, args):
    if args.type not in cfg["types"]:
        die(f"未知类型 {args.type}，可选: {', '.join(cfg['types'])}")
    if args.layer not in dict(registered_layers(cfg)):
        die(f"未知分区 {args.layer}\n[wiki] 可选分区: {', '.join(sorted(dict(registered_layers(cfg))))}\n"
            f"[wiki] 新增分区: python .wiki/scripts/wiki.py layer add <路径> --prefix <前缀> --title <名称>")
    entry_id = next_id(cfg, args.layer)
    tpl_path = ROOT / cfg["paths"]["templates"] / f"{args.type}.md"
    body = tpl_path.read_text(encoding="utf-8") if tpl_path.exists() else f"# {args.title}\n\n（正文）\n"
    meta = {
        "id": entry_id,
        "title": args.title,
        "type": args.type,
        "maturity": "draft",
        "owner": args.owner,
        "created": today_str(),
        "last_verified": None,
        "last_referenced": None,
        "reference_count": 0,
        "validations": [],
        "source": args.source or "direct",
    }
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    if tags:
        meta["tags"] = tags
    if args.type == "runbook" or args.type == "手册":
        meta["risk"] = args.risk or "medium"
    if args.type == "guideline" or args.type == "规范":
        meta["polarity"] = "recommend"
    fname = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", args.title)[:40]
    target = ROOT / args.layer / f"{entry_id}-{fname}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_frontmatter(meta) + "\n" + body, encoding="utf-8")
    append_log(cfg, "new", args.owner, f"{entry_id} {args.title} ({args.type} @ {args.layer})")
    out(f"[wiki] 已创建: {target.as_posix()}")
    out("[wiki] 提醒: 填写正文后运行 `python .wiki/scripts/wiki.py index`，并请他人 /wiki-verify")


def cmd_promote(cfg, args):
    src = Path(args.file)
    if not src.is_file():
        die(f"文件不存在: {args.file}")
    if args.to not in dict(registered_layers(cfg)):
        die(f"未知目标分区 {args.to}")
    meta, body = parse_frontmatter(src.read_text(encoding="utf-8"))
    if meta is None:
        die("源文件缺少 frontmatter")
    new_id = next_id(cfg, args.to)
    old_id = meta.get("id", src.stem)
    meta["id"] = new_id
    meta["promoted_from"] = old_id
    meta["maturity"] = "draft"
    meta["validations"] = []
    fname = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", meta.get("title", "entry"))[:40]
    target = ROOT / args.to / f"{new_id}-{fname}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_frontmatter(meta) + "\n" + body, encoding="utf-8")
    if not args.keep_source:
        src.unlink()
    append_log(cfg, "promote", args.owner, f"{old_id} → {new_id} (@{args.to})")
    cmd_index(cfg, args)
    out(f"[wiki] 转正完成: {old_id} → {target.as_posix()}（成熟度重置为 draft，需重新验证）")


# ---------------------------------------------------------- stats / init / doctor

def cmd_stats(cfg, args):
    entries = load_entries(cfg)
    if not entries:
        out("[wiki] 知识库为空")
        return
    ref_index = load_reference_index(cfg)
    levels = cfg["maturity"]["levels"]
    out(f"=== Wiki 体检 ({today_str()}) ===  总条数: {len(entries)}")
    out("\n按成熟度:")
    for lv in levels:
        n = sum(1 for e in entries if e.maturity == lv)
        out(f"  {lv:<9} {n:>3}  {'█' * n}")
    out("\n按分区:")
    for path_key, meta in layers_in_config_order(cfg):
        es = [e for e in entries if e.layer_root == path_key]
        if es:
            counts = ", ".join(f"{lv}:{sum(1 for e in es if e.maturity == lv)}" for lv in levels)
            out(f"  {path_key:<20} {len(es):>3}  ({counts})")
    top = sorted(entries, key=lambda e: -reference_count(e, ref_index))[:5]
    out("\nTop 引用:")
    for e in top:
        out(f"  {e.id}: {reference_count(e, ref_index)} 次 — {e.title}")
    verified_cnt = sum(1 for e in entries if parse_date(e.meta.get("last_verified")))
    out(f"\n验证覆盖率: {verified_cnt}/{len(entries)} ({verified_cnt * 100 // len(entries)}%)")


def cmd_init(cfg, args):
    created = []
    for path_key, meta in layers_in_config_order(cfg):
        d = ROOT / path_key
        if not d.exists():
            d.mkdir(parents=True)
            (d / "README.md").write_text(
                f"# {meta['title']}\n\n条目格式见根目录 README；目录索引由 `python .wiki/scripts/wiki.py index` 生成。\n",
                encoding="utf-8")
            created.append(d.as_posix())
    (ROOT / cfg["paths"]["pending"]).mkdir(exist_ok=True)
    (ROOT / cfg["paths"]["archive"]).mkdir(exist_ok=True)
    log_dir(cfg).mkdir(parents=True, exist_ok=True)
    if not log_file(cfg).exists():
        log_file(cfg).write_text(
            f"# Wiki 操作日志 {date.today().year}（append-only）\n格式: [日期] 事件 | 操作者 | 详情\n\n"
            f"[{today_str()}] init | system | 初始化\n", encoding="utf-8")
        created.append(log_file(cfg).as_posix())
    out(f"[wiki] init 完成，新建 {len(created)} 项" + (": " + ", ".join(created) if created else "（结构已就绪）"))
    cmd_index(cfg, args)


def cmd_doctor(cfg):
    ok = True
    for path_key in dict(layers_in_config_order(cfg)):
        good = (ROOT / path_key).is_dir()
        ok &= good
        out(f"  [{'OK ' if good else '缺失'}] {path_key}")
    tpl = ROOT / cfg["paths"]["templates"]
    out(f"  [{'OK ' if tpl.is_dir() else '缺失'}] 模板目录 {cfg['paths']['templates']}/")
    out("[wiki] doctor: " + ("一切正常" if ok else "存在缺失目录，运行 init 修复"))


# ---------------------------------------------------------- layer / type 自定义

def _norm_rel_path(p):
    return p.strip().strip("/").replace("\\", "/")


def cmd_layer(cfg, args):
    reg = dict(layers_in_config_order(cfg))
    if args.layer_cmd == "list":
        counts = {}
        for e in load_entries(cfg):
            counts[e.layer_root] = counts.get(e.layer_root, 0) + 1
        out(f"共 {len(reg)} 个分区:")
        for path_key, m in reg.items():
            out(f"  {path_key:<22} 前缀 {m['prefix']:<4} {m['title']}  ({counts.get(path_key, 0)} 条)")
        out("新增: python .wiki/scripts/wiki.py layer add <路径> --prefix <前缀> --title <名称>")
        return
    if args.layer_cmd == "add":
        path_key = _norm_rel_path(args.path)
        if not path_key or path_key.startswith("..") or ":" in path_key:
            die("非法路径，应为仓库内相对路径（如 infra/monitoring）")
        if path_key in cfg["layers"]:
            die(f"分区已存在: {path_key}")
        prefix = (args.prefix or "").strip().upper()
        if not re.match(r"^[A-Z0-9]{1,6}$", prefix):
            die("prefix 需为 1-6 位字母数字（用作条目编号前缀，如 MON）")
        if any(m.get("prefix") == prefix for m in cfg["layers"].values()):
            die(f"前缀已被其他分区占用: {prefix}")
        cfg["layers"][path_key] = {"path": path_key, "prefix": prefix, "active": True,
                                   "title": args.title, "note": args.note or ""}
        save_config(cfg)
        d = ROOT / path_key
        existed = d.is_dir()
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "README.md").exists():
            (d / "README.md").write_text(
                f"# {args.title}\n\n条目格式见根目录 README；目录索引由 `python .wiki/scripts/wiki.py index` 生成。\n",
                encoding="utf-8")
        cmd_index(cfg, args)
        out(f"[wiki] 分区已添加: {path_key}（前缀 {prefix}）" + ("，已接管现有目录" if existed else ""))
        out(f"[wiki] 用法: python .wiki/scripts/wiki.py new <类型> \"标题\" --layer {path_key}")
        return
    if args.layer_cmd == "rm":
        path_key = _norm_rel_path(args.path)
        if path_key not in cfg["layers"]:
            die(f"未注册的分区: {path_key}")
        d = ROOT / path_key
        if d.is_dir():
            strays = [f for f in d.rglob("*.md") if f.name not in ("README.md", "catalog.md")]
            if strays:
                die(f"分区下还有 {len(strays)} 个条目（如 {strays[0].relative_to(ROOT).as_posix()}），"
                    f"先迁移（promote 或 mv）再删除")
        del cfg["layers"][path_key]
        save_config(cfg)
        for junk in ("catalog.md", "README.md"):
            p = d / junk
            if p.exists():
                p.unlink()
        try:
            d.rmdir()
        except OSError:
            pass
        cmd_index(cfg, args)
        out(f"[wiki] 分区已移除: {path_key}")


def cmd_type(cfg, args):
    if args.type_cmd == "list":
        entries = load_entries(cfg)
        out(f"共 {len(cfg['types'])} 种类型:")
        for k, m in cfg["types"].items():
            n = sum(1 for e in entries if e.type == k)
            out(f"  {k:<12} {m.get('title', '')}  ({n} 条)")
        out("新增: python .wiki/scripts/wiki.py type add <key> --title <名称>")
        return
    if args.type_cmd == "add":
        key = args.key.strip()
        if not re.match(r"^[\w][\w-]*$", key, re.UNICODE):
            die("类型 key 需以字母或中文开头，仅含 字母/数字/中文/_/-（如 postmortem 或 复盘）")
        if key in cfg["types"]:
            die(f"类型已存在: {key}")
        cfg["types"][key] = {"title": args.title, "desc": args.desc or ""}
        save_config(cfg)
        tpl = ROOT / cfg["paths"]["templates"] / f"{key}.md"
        if not tpl.exists():
            tpl.write_text(
                f"# <标题>\n\n> {args.title}类知识。建议写清：适用场景、内容、证据或示例。\n\n（正文）\n",
                encoding="utf-8")
        out(f"[wiki] 类型已添加: {key}（模板 templates/{key}.md）")
        out(f"[wiki] 用法: python .wiki/scripts/wiki.py new {key} \"标题\" --layer <分区>")
        return
    if args.type_cmd == "rm":
        key = args.key.strip()
        if key not in cfg["types"]:
            die(f"未注册的类型: {key}")
        used = [e.id for e in load_entries(cfg) if e.type == key]
        if used:
            die(f"仍有 {len(used)} 条条目使用该类型（如 {', '.join(used[:3])}），先改 type 再删除")
        del cfg["types"][key]
        save_config(cfg)
        out(f"[wiki] 类型已移除: {key}（模板文件保留在 templates/，可手工删）")


def main():
    cfg = load_config()
    p = argparse.ArgumentParser(prog="wiki", description="团队 wiki 引擎")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化目录结构/日志/索引")
    sub.add_parser("index", help="重建索引")
    sub.add_parser("stats", help="体检报告")

    pl = sub.add_parser("lint", help="膨胀治理检查")
    pl.add_argument("--fix", action="store_true", help="自动修复安全项（重建索引）")

    ps = sub.add_parser("search", help="预算受控检索")
    ps.add_argument("query", nargs="+")
    ps.add_argument("--type")
    ps.add_argument("--maturity")
    ps.add_argument("--risk")
    ps.add_argument("--limit", type=int, default=5)
    ps.add_argument("--full", type=int, default=0)
    ps.add_argument("--reference", metavar="CTX")

    pv = sub.add_parser("verify", help="记录人工验证")
    pv.add_argument("id")
    pv.add_argument("--by", required=True)
    pv.add_argument("--project")
    pv.add_argument("--promote", action="store_true")

    pr = sub.add_parser("reference", help="记录引用")
    pr.add_argument("ids", nargs="+")
    pr.add_argument("--in", dest="in_context", default="manual")

    sub.add_parser("decay", help="成熟度衰减与归档")

    pn = sub.add_parser("new", help="新建条目")
    pn.add_argument("type", choices=list(cfg["types"]))
    pn.add_argument("title")
    pn.add_argument("--layer", required=True)
    pn.add_argument("--owner", default=os_user())
    pn.add_argument("--tags")
    pn.add_argument("--risk", choices=["low", "medium", "high"])
    pn.add_argument("--source")

    pp = sub.add_parser("promote", help="pending 候选/项目条目转正到目标分区")
    pp.add_argument("--file", required=True)
    pp.add_argument("--to", required=True)
    pp.add_argument("--keep-source", action="store_true")
    pp.add_argument("--owner", default=os_user())

    sub.add_parser("doctor", help="自检")

    pg = sub.add_parser("layer", help="分区管理（自定义分层）")
    gs = pg.add_subparsers(dest="layer_cmd", required=True)
    gs.add_parser("list", help="列出全部分区")
    ga = gs.add_parser("add", help="新增分区：自动建目录/写配置/刷索引")
    ga.add_argument("path", help="仓库内相对路径，如 infra/monitoring")
    ga.add_argument("--prefix", required=True, help="编号前缀，1-6 位字母数字，如 MON")
    ga.add_argument("--title", required=True, help="展示名")
    ga.add_argument("--note")
    gr = gs.add_parser("rm", help="移除分区（仅允许空分区）")
    gr.add_argument("path")

    tg = sub.add_parser("type", help="类型管理（自定义类型）")
    ts = tg.add_subparsers(dest="type_cmd", required=True)
    ts.add_parser("list", help="列出全部类型")
    ta = ts.add_parser("add", help="新增类型：自动生成条目模板")
    ta.add_argument("key", help="类型标识，字母开头，如 postmortem")
    ta.add_argument("--title", required=True, help="展示名")
    ta.add_argument("--desc")
    tr = ts.add_parser("rm", help="移除类型（仅允许未被条目使用的类型）")
    tr.add_argument("key")

    args = p.parse_args()
    {"init": cmd_init, "index": cmd_index, "lint": cmd_lint, "search": cmd_search,
     "verify": cmd_verify, "reference": cmd_reference, "decay": cmd_decay,
     "new": cmd_new, "promote": cmd_promote, "stats": cmd_stats,
     "layer": cmd_layer, "type": cmd_type,
     "doctor": lambda c, a: cmd_doctor(c)}[args.cmd](cfg, args)


if __name__ == "__main__":
    main()
