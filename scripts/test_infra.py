#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""infra.py 核心行为单测（stdlib unittest，零依赖）"""
import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "infra.py"

spec = importlib.util.spec_from_file_location("infra", SCRIPT)
infra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(infra)

ORIG_ROOT = infra.ROOT

CFG = {
    "budgets": {"default": {"dirs": 2, "full": 5, "hint": ""}},
    "maturity": {"levels": ["draft", "verified", "proven"]},
    "decay": {"proven_months": 12, "demote_verified_months": 6,
              "archive_draft_months": 6, "registry_exempt": True},
    "lint": {
        "runbook_requires": ["前置条件", "操作步骤", "验证", "回滚"],
        "playbook_requires": ["症状", "排查", "常见根因", "升级"],
        "adr_requires": ["背景", "决策", "备选", "影响"],
        "case_requires": ["现象", "根因", "改进"],
        "faq_requires": ["Q1"],
        "architecture_requires": ["mermaid"],
        "kinds_requiring_risk": ["runbook", "playbook"],
        "registry_required": ["resource_type", "name", "env", "owner",
                              "entrypoints", "knowledge"],
        "registry_review_days": 90,
    },
}

FM = ("---\ntitle: {title}\nowner: tester\nkind: {kind}\nmaturity: {maturity}\n"
      "risk: {risk}\ntags: [{tags}]\nrelated: []\ncreated: 2026-08-18\n"
      "last_verified: null\nlast_reviewed: null\n---\n\n{body}\n")

RUNBOOK_BODY = ("# 域名申请\n## 目标\nx\n## 前置条件\nx\n## 操作步骤\nx\n"
                "## 验证\nx\n## 回滚\nx\n")


class TmpRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        infra.ROOT = Path(self.tmp.name)
        self.buf = []
        infra.out = self.buf.append

    def tearDown(self):
        infra.ROOT = ORIG_ROOT
        self.tmp.cleanup()

    def write(self, rel, content):
        p = infra.ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    def ns(self, **kw):
        return argparse.Namespace(**kw)


class TestYamlSubset(unittest.TestCase):
    def test_nested_block_and_inline_lists(self):
        data = infra.parse_yaml(
            "owner:\n  team: infra\nknowledge:\n  runbooks:\n"
            "    - 手册/a.md\n    - 手册/b.md\ntags: [mongo, prod]\n"
            "list2:\n- x.md\nenv: prod\n")
        self.assertEqual(data["owner"]["team"], "infra")
        self.assertEqual(data["knowledge"]["runbooks"], ["手册/a.md", "手册/b.md"])
        self.assertEqual(data["tags"], ["mongo", "prod"])
        self.assertEqual(data["list2"], ["x.md"])
        self.assertEqual(data["env"], "prod")


class TestScore(TmpRepoTestCase):
    def test_body_only_keyword_scores(self):
        e = infra.Entry(Path("排障/x.md"),
                        {"title": "无关标题", "tags": []},
                        "正文独有词xyzabc在这里")
        self.assertGreater(infra.score_entry(e, infra._tokens("独有词xyzabc")), 0)

    def test_title_weighted_higher_than_body(self):
        e1 = infra.Entry(Path("排障/a.md"), {"title": "独有词xyzabc", "tags": []}, "其他")
        e2 = infra.Entry(Path("排障/b.md"), {"title": "其他", "tags": []}, "独有词xyzabc")
        t = infra._tokens("独有词xyzabc")
        self.assertGreater(infra.score_entry(e1, t), infra.score_entry(e2, t))


class TestLint(TmpRepoTestCase):
    def run_lint(self):
        try:
            infra.cmd_lint(CFG, self.ns())
            return 0
        except SystemExit as ex:
            return ex.code

    def test_valid_runbook_passes(self):
        self.write("手册/domain-apply.md",
                   FM.format(title="域名申请", kind="runbook", maturity="verified",
                             risk="medium", tags="dns", body=RUNBOOK_BODY))
        self.assertEqual(self.run_lint(), 0)

    def test_runbook_missing_risk_fails(self):
        content = FM.format(title="域名申请", kind="runbook", maturity="draft",
                            risk="medium", tags="", body=RUNBOOK_BODY)
        content = content.replace("risk: medium\n", "")
        self.write("手册/domain-apply.md", content)
        self.assertEqual(self.run_lint(), 1)

    def test_runbook_missing_section_fails(self):
        body = RUNBOOK_BODY.replace("## 回滚\nx\n", "")
        self.write("手册/domain-apply.md",
                   FM.format(title="t", kind="runbook", maturity="draft",
                             risk="low", tags="", body=body))
        self.assertEqual(self.run_lint(), 1)

    def test_broken_related_fails(self):
        content = FM.format(title="t", kind="runbook", maturity="draft",
                            risk="low", tags="", body=RUNBOOK_BODY)
        content = content.replace("related: []", "related: [排障/nope.md]")
        self.write("手册/domain-apply.md", content)
        self.assertEqual(self.run_lint(), 1)

    def test_kind_dir_mismatch_fails(self):
        self.write("排障/not-a-runbook.md",
                   FM.format(title="t", kind="runbook", maturity="draft",
                             risk="low", tags="", body=RUNBOOK_BODY))
        self.assertEqual(self.run_lint(), 1)

    def test_inbox_draft_any_kind_ok(self):
        self.write("草稿箱/anything.md",
                   FM.format(title="t", kind="runbook", maturity="draft",
                             risk="low", tags="", body=RUNBOOK_BODY))
        self.assertEqual(self.run_lint(), 0)

    def test_registry_missing_required_field_fails(self):
        self.write("台账/数据库/mongo-x.yaml",
                   "resource_type: database\nname: mongo-x\nenv: prod\n")
        self.assertEqual(self.run_lint(), 1)

    def test_registry_stale_review_warns_not_fails(self):
        self.write("台账/数据库/mongo-x.yaml",
                   "resource_type: database\nname: mongo-x\nenv: prod\nowner:\n  team: t\n"
                   "entrypoints:\n  console: x\nknowledge:\n  runbooks: []\n"
                   "last_reviewed: \"2026-01-01\"\n")
        self.assertEqual(self.run_lint(), 0)
        self.assertTrue(any("未复审" in m for m in self.buf))

    def test_registry_knowledge_broken_link_fails(self):
        self.write("台账/数据库/mongo-x.yaml",
                   "resource_type: database\nname: mongo-x\nenv: prod\nowner:\n  team: t\n"
                   "entrypoints:\n  console: x\nknowledge:\n  runbooks:\n"
                   "  - 手册/nope.md\nlast_reviewed: \"2026-08-01\"\n")
        self.assertEqual(self.run_lint(), 1)


class TestDecay(TmpRepoTestCase):
    def make(self, rel, maturity, created):
        return self.write(rel, FM.format(title="t", kind="runbook", maturity=maturity,
                                          risk="low", tags="", body=RUNBOOK_BODY)
                          .replace("created: 2026-08-18", f"created: {created}"))

    def test_verified_stale_demotes(self):
        p = self.make("手册/old.md", "verified", "2025-01-01")
        infra.cmd_decay(CFG, self.ns(fix=False))
        self.assertIn("maturity: draft", p.read_text(encoding="utf-8"))

    def test_recent_reference_prevents_decay(self):
        p = self.make("手册/fresh.md", "verified", "2025-01-01")
        infra.append_reference("手册/fresh.md", "test")
        infra.cmd_decay(CFG, self.ns(fix=False))
        self.assertIn("maturity: verified", p.read_text(encoding="utf-8"))

    def test_stale_draft_archive_needs_fix(self):
        p = self.make("手册/zombie.md", "draft", "2025-01-01")
        infra.cmd_decay(CFG, self.ns(fix=False))
        self.assertTrue(p.exists())
        self.assertTrue(any("可归档" in m for m in self.buf))
        infra.cmd_decay(CFG, self.ns(fix=True))
        self.assertFalse(p.exists())
        self.assertTrue((infra.ROOT / "归档" / "2026" / "zombie.md").exists())

    def test_registry_exempt(self):
        self.write("台账/数据库/mongo-x.yaml",
                   "resource_type: database\nname: mongo-x\nenv: prod\nowner:\n  team: t\n"
                   "entrypoints:\n  console: x\nknowledge:\n  runbooks: []\n"
                   "last_reviewed: \"2025-01-01\"\n")
        infra.cmd_decay(CFG, self.ns(fix=True))
        self.assertTrue((infra.ROOT / "台账/数据库/mongo-x.yaml").exists())


class TestReferenceSidecar(TmpRepoTestCase):
    def test_reference_writes_sidecar_not_entry(self):
        p = self.write("排障/disk-full.md",
                       FM.format(title="磁盘满", kind="playbook", maturity="verified",
                                 risk="low", tags="磁盘", body="# 症状\nx\n"))
        before = p.read_text(encoding="utf-8")
        infra.cmd_reference(CFG, self.ns(paths=["排障/disk-full.md"], in_context="unit"))
        self.assertEqual(before, p.read_text(encoding="utf-8"))
        refs = infra.ROOT / ".infra" / f"refs-{infra.date.today().year}.jsonl"
        self.assertTrue(refs.is_file())
        rec = json.loads(refs.read_text(encoding="utf-8").strip())
        self.assertEqual(rec["ref"], "排障/disk-full.md")
        self.assertEqual(rec["context"], "unit")


class TestNew(TmpRepoTestCase):
    def test_new_scaffold(self):
        tpl = infra.ROOT / "templates" / "runbook.md"
        tpl.parent.mkdir(parents=True, exist_ok=True)
        tpl.write_text(
            "---\ntitle: \"\"\nowner: \"\"\nkind: runbook\nmaturity: draft\n"
            "risk: medium\ntags: []\nrelated: []\ncreated: \"\"\n"
            "last_verified: null\nlast_reviewed: null\n---\n\n## 前置条件\n",
            encoding="utf-8")
        infra.cmd_new(CFG, self.ns(kind="runbook", slug="fw-apply", title="防火墙申请",
                                   tags="网络,防火墙"))
        dest = infra.ROOT / "草稿箱" / "fw-apply.md"
        self.assertTrue(dest.is_file())
        meta, _ = infra.parse_frontmatter(dest.read_text(encoding="utf-8"))
        self.assertEqual(meta["title"], "防火墙申请")
        self.assertEqual(meta["created"], infra.today_str())
        self.assertEqual(meta["tags"], ["网络", "防火墙"])


if __name__ == "__main__":
    unittest.main()
