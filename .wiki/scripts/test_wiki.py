#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wiki.py 核心行为单测（stdlib unittest，零依赖）"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".wiki" / "scripts" / "wiki.py"


def load_wiki_module():
    spec = importlib.util.spec_from_file_location("wiki", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


wiki = load_wiki_module()


def make_entry(entry_id, title, body, entry_type="踩坑", tags=None, polarity=None, layer="通用"):
    meta = {
        "id": entry_id,
        "title": title,
        "type": entry_type,
        "maturity": "draft",
        "owner": "test",
        "created": "2026-08-17",
        "tags": tags or [],
    }
    if polarity:
        meta["polarity"] = polarity
    path = Path(layer) / f"{entry_id}.md"
    return wiki.Entry(path, meta, body, layer)


class TestScoreEntry(unittest.TestCase):
    def test_body_only_keyword_scores(self):
        e = make_entry("TEC-001", "无关标题", "正文独有词xyzabc在这里")
        terms = wiki._tokens("独有词xyzabc")
        self.assertGreater(wiki.score_entry(e, terms), 0)

    def test_title_weighted_higher_than_body(self):
        e_title = make_entry("TEC-001", "独有词xyzabc", "其他内容")
        e_body = make_entry("TEC-002", "其他标题", "独有词xyzabc")
        terms = wiki._tokens("独有词xyzabc")
        self.assertGreater(wiki.score_entry(e_title, terms), wiki.score_entry(e_body, terms))


class TestGuidelineConflicts(unittest.TestCase):
    def test_chinese_guideline_type_detected(self):
        a = make_entry("TEC-001", "提交前必须跑测试", "理由\n", entry_type="规范",
                       tags=["ci"], polarity="recommend")
        b = make_entry("NET-001", "提交前必须跑测试", "理由\n", entry_type="规范",
                       tags=["ci"], polarity="avoid", layer="基础设施/网络")
        conflicts = wiki.find_guideline_conflicts([a, b])
        self.assertEqual(len(conflicts), 1)
        self.assertIn("TEC-001", conflicts[0])
        self.assertIn("NET-001", conflicts[0])

    def test_type_alias_matches(self):
        self.assertTrue(wiki.type_matches("规范", "guideline"))
        self.assertTrue(wiki.type_matches("手册", "runbook"))


class TestReferenceSidecar(unittest.TestCase):
    def test_reference_does_not_modify_entry_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki.ROOT = tmp_path
            cfg = {
                "paths": {"log": ".wiki/logs", "pending": "pending", "archive": "archive",
                          "catalog": "catalog.md", "templates": ".wiki/templates"},
                "layers": {"通用": {"path": "通用", "prefix": "TEC", "active": True}},
                "types": {"踩坑": {}},
                "maturity": {"levels": ["draft", "verified", "proven"]},
            }
            layer = tmp_path / "通用"
            layer.mkdir(parents=True)
            entry_path = layer / "TEC-001-test.md"
            original = "---\nid: TEC-001\ntitle: t\ntype: 踩坑\nmaturity: draft\nowner: x\ncreated: 2026-08-17\n---\n\nbody\n"
            entry_path.write_text(original, encoding="utf-8")
            before = entry_path.read_text(encoding="utf-8")

            wiki._do_reference(cfg, ["TEC-001"], "unit-test")

            after = entry_path.read_text(encoding="utf-8")
            self.assertEqual(before, after)
            refs = tmp_path / ".wiki" / "logs" / f"refs-{wiki.date.today().year}.jsonl"
            self.assertTrue(refs.is_file())
            line = json.loads(refs.read_text(encoding="utf-8").strip())
            self.assertEqual(line["id"], "TEC-001")
            self.assertEqual(line["context"], "unit-test")

    def test_anchor_clock_prefers_sidecar(self):
        e = make_entry("TEC-001", "t", "b")
        ref_index = {"TEC-001": {"count": 2, "last_date": wiki.parse_date("2026-08-10")}}
        self.assertEqual(wiki.entry_anchor_clock(e, ref_index).isoformat(), "2026-08-10")


class TestEmptyCatalogMessage(unittest.TestCase):
    def test_stats_empty_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki.ROOT = Path(tmp)
            cfg = {"paths": {"log": ".wiki/logs"}, "layers": {}, "types": {},
                   "maturity": {"levels": ["draft"]}}
            buf = []
            wiki.out = buf.append
            wiki.cmd_stats(cfg, None)
            self.assertEqual(buf[0], "[wiki] 知识库为空")


if __name__ == "__main__":
    unittest.main()
