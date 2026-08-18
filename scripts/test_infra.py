#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""infra.py 核心行为单测（stdlib unittest，零依赖）· 方案D域制"""
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
    "automation_levels": ["L0", "L1", "L2", "L3"],
    "maturity": {"levels": ["draft", "verified", "proven"]},
    "decay": {"proven_months": 12, "demote_verified_months": 6},
    "domains": {
        "storage": {"path": "knowledge/06-存储", "title": "存储"},
        "network": {"path": "knowledge/04-网络管理", "title": "网络"},
    },
    "lint": {
        "runbook_requires": ["前置条件", "操作步骤", "验证", "回滚"],
        "playbook_requires": ["症状", "排查", "常见根因", "升级"],
        "adr_requires": ["背景", "决策", "备选", "影响"],
        "case_requires": ["现象", "根因", "改进"],
        "faq_requires": ["Q1"],
        "architecture_requires": ["mermaid"],
        "risk_kinds": ["runbook", "playbook"],
        "automation_kinds": ["runbook", "playbook"],
        "registry_required": ["resource_type", "name", "env", "owner", "entrypoints"],
        "registry_review_days": 90,
        "manifest_risk_levels": ["readonly", "change"],
    },
    "paths": {
        "knowledge": "knowledge", "manifest": "scripts/manifest.yaml",
        "symptom_index": "问题定位索引.md", "domain_routes": "域路由表.yaml",
        "reports": "reports", "skills": ".claude/skills",
    },
}

FM = ("---\ntitle: {title}\nowner: tester\nkind: {kind}\nmaturity: {maturity}\n"
      "risk: {risk}\nautomation: L0\nsymptoms: [{symptoms}]\ntags: []\nrelated: []\n"
      "created: 2026-08-18\nlast_verified: null\nlast_reviewed: null\n---\n\n{body}\n")

PLAYBOOK_BODY = "# 症状\nx\n## 排查路径\nx\n## 常见根因\nx\n## 升级条件\nx\n"
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
        p.write_text(content, encoding="utf-8", newline="\n")
        return p

    def ns(self, **kw):
        return argparse.Namespace(**kw)

    def make_playbook(self, rel="knowledge/06-存储/问题定位/磁盘满.md", **kw):
        kw.setdefault("title", "磁盘满")
        kw.setdefault("kind", "playbook")
        kw.setdefault("maturity", "draft")
        kw.setdefault("risk", "low")
        kw.setdefault("symptoms", "磁盘满")
        kw.setdefault("body", PLAYBOOK_BODY)
        return self.write(rel, FM.format(**kw))


class TestYamlSubset(unittest.TestCase):
    def test_manifest_list_of_maps(self):
        data = infra.parse_yaml(
            "- name: a\n  domain: storage\n  path: p1\n"
            "- name: b\n  domain: k8s\n  path: p2\n")
        self.assertEqual(data, [{"name": "a", "domain": "storage", "path": "p1"},
                                {"name": "b", "domain": "k8s", "path": "p2"}])

    def test_inventory_resources(self):
        data = infra.parse_yaml(
            "resources:\n  - resource_type: database\n    name: mongo-x\n"
            "    owner:\n      team: t\n    entrypoints:\n      console: c\n")
        r = data["resources"][0]
        self.assertEqual(r["resource_type"], "database")
        self.assertEqual(r["name"], "mongo-x")
        self.assertEqual(r["owner"]["team"], "t")
        self.assertEqual(r["entrypoints"]["console"], "c")

    def test_same_indent_block_list(self):
        data = infra.parse_yaml("knowledge:\n  runbooks:\n- a.md\n- b.md\ntags: [x, y]\n")
        self.assertEqual(data["knowledge"]["runbooks"], ["a.md", "b.md"])
        self.assertEqual(data["tags"], ["x", "y"])


class TestLocationRules(TmpRepoTestCase):
    def test_rules(self):
        f = lambda p: infra.expected_kinds_for(CFG, Path(p))  # noqa: E731
        self.assertEqual(f("knowledge/06-存储/问题定位/x.md"), {"playbook"})
        self.assertEqual(f("knowledge/06-存储/复盘/x.md"), {"case"})
        self.assertEqual(f("knowledge/06-存储/方案设计/0001-x.md"), {"adr"})
        self.assertEqual(f("knowledge/06-存储/批量VM操作.md"), {"runbook", "reference"})
        self.assertEqual(f("knowledge/06-存储/faq.md"), {"faq"})
        self.assertEqual(f("knowledge/06-存储/architecture-链路.md"), {"architecture"})
        self.assertEqual(f("knowledge/06-存储/inventory.yaml"), {"registry"})
        self.assertEqual(f("knowledge/06-存储/子目录/other.yaml"), set())
        self.assertIsNone(f("README.md"))

    def test_domain_of(self):
        key, prefix = infra.domain_of(CFG, Path("knowledge/06-存储/问题定位/x.md"))
        self.assertEqual((key, prefix), ("storage", "knowledge/06-存储"))
        self.assertEqual(infra.domain_of(CFG, Path("docs/x.md")), (None, None))


class TestLint(TmpRepoTestCase):
    def run_lint(self):
        try:
            infra.cmd_lint(CFG, self.ns())
            return 0
        except SystemExit as ex:
            return ex.code

    def setUp(self):
        super().setUp()
        self.write("scripts/manifest.yaml", "")  # 空 manifest 合法
        self.make_playbook()

    def test_valid_playbook_passes(self):
        self.assertEqual(self.run_lint(), 0)

    def test_playbook_symptoms_missing_warns_only(self):
        p = infra.ROOT / "knowledge/06-存储/问题定位/磁盘满.md"
        p.write_text(p.read_text(encoding="utf-8").replace("symptoms: [磁盘满]",
                                                           "symptoms: null"),
                     encoding="utf-8")
        self.assertEqual(self.run_lint(), 0)
        self.assertTrue(any("symptoms" in m for m in self.buf))

    def test_runbook_in_wentiweizhi_fails(self):
        self.make_playbook(rel="knowledge/06-存储/问题定位/域名申请.md", title="域名",
                           kind="runbook", risk="medium", symptoms="", body=RUNBOOK_BODY)
        self.assertEqual(self.run_lint(), 1)
        self.assertTrue(any("与位置不符" in m for m in self.buf))

    def test_bad_automation_fails(self):
        p = infra.ROOT / "knowledge/06-存储/问题定位/磁盘满.md"
        p.write_text(p.read_text(encoding="utf-8").replace("automation: L0",
                                                           "automation: L9"),
                     encoding="utf-8")
        self.assertEqual(self.run_lint(), 1)

    def test_script_not_in_manifest_fails(self):
        self.write("scripts/x.sh", "#!/bin/bash\n")
        p = infra.ROOT / "knowledge/06-存储/问题定位/磁盘满.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "tags: []", "tags: []\nscript: scripts/x.sh"), encoding="utf-8")
        self.assertEqual(self.run_lint(), 1)
        self.assertTrue(any("manifest 登记" in m for m in self.buf))

    def test_skill_not_exist_fails(self):
        p = infra.ROOT / "knowledge/06-存储/问题定位/磁盘满.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "tags: []", "tags: []\nskill: storage/nope"), encoding="utf-8")
        self.assertEqual(self.run_lint(), 1)

    def test_manifest_bad_path_fails(self):
        self.write("scripts/manifest.yaml",
                   "- name: x\n  domain: storage\n  path: scripts/nope.sh\n"
                   "  risk_level: readonly\n  entry_command: \"x\"\n"
                   "  related_doc: knowledge/06-存储/问题定位/磁盘满.md\n")
        self.assertEqual(self.run_lint(), 1)

    def test_manifest_change_requires_dryrun(self):
        self.write("scripts/change.sh", "#!/bin/bash\n# no dry run here\n")
        self.write("scripts/manifest.yaml",
                   "- name: c\n  domain: storage\n  path: scripts/change.sh\n"
                   "  risk_level: change\n  entry_command: \"x\"\n"
                   "  related_doc: knowledge/06-存储/问题定位/磁盘满.md\n")
        self.assertEqual(self.run_lint(), 1)
        self.assertTrue(any("dry-run" in m for m in self.buf))

    def test_inventory_missing_field_fails(self):
        self.write("knowledge/06-存储/inventory.yaml",
                   "resources:\n  - resource_type: storage\n    name: minio\n")
        self.assertEqual(self.run_lint(), 1)

    def test_inventory_stale_review_warns_only(self):
        self.write("knowledge/06-存储/inventory.yaml",
                   "resources:\n  - resource_type: storage\n    name: minio\n    env: prod\n"
                   "    owner:\n      team: t\n    entrypoints:\n      console: c\n"
                   "    last_reviewed: \"2026-01-01\"\n")
        self.assertEqual(self.run_lint(), 0)
        self.assertTrue(any("未复审" in m for m in self.buf))


class TestDecay(TmpRepoTestCase):
    def make(self, rel, maturity, created):
        return self.write(rel, FM.format(title="t", kind="runbook", maturity=maturity,
                                          risk="low", symptoms="", body=RUNBOOK_BODY)
                          .replace("created: 2026-08-18", f"created: {created}")
                          .replace("automation: L0\n", ""))

    def test_verified_stale_demotes(self):
        p = self.make("knowledge/04-网络管理/old.md", "verified", "2025-01-01")
        infra.cmd_decay(CFG, self.ns())
        self.assertIn("maturity: draft", p.read_text(encoding="utf-8"))

    def test_recent_reference_prevents_decay(self):
        p = self.make("knowledge/04-网络管理/fresh.md", "verified", "2025-01-01")
        infra.append_reference("knowledge/04-网络管理/fresh.md", "test")
        infra.cmd_decay(CFG, self.ns())
        self.assertIn("maturity: verified", p.read_text(encoding="utf-8"))

    def test_stale_draft_suggests_delete_but_keeps_file(self):
        p = self.make("knowledge/04-网络管理/zombie.md", "draft", "2025-01-01")
        infra.cmd_decay(CFG, self.ns())
        self.assertTrue(p.exists())
        self.assertTrue(any("建议删除" in m for m in self.buf))


class TestReferenceSidecar(TmpRepoTestCase):
    def test_reference_writes_sidecar_not_entry(self):
        p = self.make_playbook(rel="knowledge/06-存储/问题定位/磁盘满.md")
        before = p.read_text(encoding="utf-8")
        rel = "knowledge/06-存储/问题定位/磁盘满.md"
        infra.cmd_reference(CFG, self.ns(paths=[rel], in_context="unit"))
        self.assertEqual(before, p.read_text(encoding="utf-8"))
        refs = infra.ROOT / ".infra" / f"refs-{infra.date.today().year}.jsonl"
        self.assertTrue(refs.is_file())
        rec = json.loads(refs.read_text(encoding="utf-8").strip())
        self.assertEqual(rec["ref"], rel)
        self.assertEqual(rec["context"], "unit")


class TestIndex(TmpRepoTestCase):
    def test_generates_routing_trio(self):
        self.write("scripts/manifest.yaml", "")
        self.make_playbook()
        infra.cmd_index(CFG, self.ns())
        routes = (infra.ROOT / "域路由表.yaml").read_text(encoding="utf-8")
        self.assertIn("storage: knowledge/06-存储", routes)
        sym = (infra.ROOT / "问题定位索引.md").read_text(encoding="utf-8")
        self.assertIn("磁盘满", sym)
        self.assertIn("问题定位/磁盘满.md", sym)
        idx = (infra.ROOT / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("knowledge/06-存储/INDEX.md", idx)
        self.assertTrue((infra.ROOT / "knowledge/06-存储/INDEX.md").exists())


class TestNew(TmpRepoTestCase):
    def test_new_playbook_goes_to_wentiweizhi(self):
        tpl = infra.ROOT / "templates" / "playbook.md"
        tpl.parent.mkdir(parents=True, exist_ok=True)
        tpl.write_text(
            "---\ntitle: \"\"\nowner: \"\"\nkind: playbook\nmaturity: draft\n"
            "risk: low\nsymptoms: []\ntags: []\nrelated: []\ncreated: \"\"\n"
            "last_verified: null\nlast_reviewed: null\n---\n\n## 症状\n",
            encoding="utf-8", newline="\n")
        infra.cmd_new(CFG, self.ns(kind="playbook", slug="磁盘满", domain="storage",
                                   title="磁盘满排查", tags="磁盘,存储"))
        dest = infra.ROOT / "knowledge/06-存储/问题定位/磁盘满.md"
        self.assertTrue(dest.is_file())
        meta, _ = infra.parse_frontmatter(dest.read_text(encoding="utf-8"))
        self.assertEqual(meta["title"], "磁盘满排查")
        self.assertEqual(meta["created"], infra.today_str())

    def test_new_unknown_domain_fails(self):
        with self.assertRaises(SystemExit):
            infra.cmd_new(CFG, self.ns(kind="playbook", slug="x", domain="nope"))


class TestScore(TmpRepoTestCase):
    def test_title_weighted_higher_than_body(self):
        e1 = infra.Entry(Path("knowledge/x/a.md"), {"title": "独有词xyzabc", "tags": []}, "其他")
        e2 = infra.Entry(Path("knowledge/x/b.md"), {"title": "其他", "tags": []}, "独有词xyzabc")
        t = infra._tokens("独有词xyzabc")
        self.assertGreater(infra.score_entry(e1, t), infra.score_entry(e2, t))


if __name__ == "__main__":
    unittest.main()
