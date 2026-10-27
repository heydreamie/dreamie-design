import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_skill.py"
MODULES = ("layout", "color", "traditional-color", "pattern", "art-analysis", "ai-style")


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "dreamie-design"
        self.root.mkdir()
        links = []
        for module in MODULES:
            folder = self.root / "references" / module
            folder.mkdir(parents=True)
            (folder / "guide.md").write_text("[Methods](methods.md)\n[Sources](sources.md)\n", encoding="utf-8")
            (folder / "methods.md").write_text("Original method notes.\n", encoding="utf-8")
            (folder / "sources.md").write_text("Bibliographic notes and PDF page numbers only.\n", encoding="utf-8")
            links.append(f"[{module}](references/{module}/guide.md)")
        (self.root / "SKILL.md").write_text(
            "---\nname: dreamie-design\ndescription: Use when visual design is requested.\n---\n\n"
            + "\n".join(links), encoding="utf-8"
        )

    def run_check(self, *extra):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(CHECKER), str(self.root), *map(str, extra)],
            text=True, capture_output=True, encoding="utf-8"
        )

    def assert_rejected(self, phrase):
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(phrase, result.stderr.lower())

    def test_valid_bundle_passes(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_broken_reference_is_rejected(self):
        (self.root / "references/layout/guide.md").write_text("[Missing](missing.md)", encoding="utf-8")
        self.assert_rejected("broken link")

    def test_private_host_path_is_rejected(self):
        private_path = "C:" + "/Users/example/private.pdf"
        (self.root / "references/color/sources.md").write_text(private_path, encoding="utf-8")
        self.assert_rejected("private path")

    def test_raw_book_is_rejected(self):
        (self.root / "references/book.pdf").write_bytes(b"not a distributable source")
        self.assert_rejected("not distributable")

    def test_secret_like_value_is_rejected(self):
        token_fixture = "ghp_" + "A" * 30
        (self.root / "references/color/methods.md").write_text(token_fixture, encoding="utf-8")
        self.assert_rejected("secret-like value")

    def test_missing_module_reference_is_rejected(self):
        (self.root / "references/pattern/methods.md").unlink()
        self.assert_rejected("missing required reference")

    def test_nested_skill_entry_is_rejected(self):
        (self.root / "references/pattern/SKILL.md").write_text("unexpected nested entry", encoding="utf-8")
        self.assert_rejected("nested skill entry")

    def test_personal_email_is_rejected(self):
        (self.root / "references/color/sources.md").write_text("person" + "@example.com", encoding="utf-8")
        self.assert_rejected("email address")

    def test_network_share_path_is_rejected(self):
        (self.root / "references/color/sources.md").write_text(
            "\\\\private-host\\share\\source.txt", encoding="utf-8"
        )
        self.assert_rejected("private path")

    def test_sensitive_json_asset_is_rejected(self):
        (self.root / "assets").mkdir()
        (self.root / "assets/config.json").write_text(
            '{"path":"C:' + '/Users/example/private", "token":"ghp_' + "A" * 30 + '"}',
            encoding="utf-8"
        )
        self.assert_rejected("secret-like value")

    def test_raw_ocr_text_asset_is_rejected(self):
        (self.root / "assets").mkdir()
        (self.root / "assets/full-ocr.txt").write_text("Raw source text", encoding="utf-8")
        self.assert_rejected("raw source text")

    def test_archive_cannot_overwrite_repository_files(self):
        for relative in ("scripts/check_skill.py", "tests/test_package.py", ".git/config"):
            with self.subTest(path=relative):
                destination = self.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"preserve this repository file")
                result = self.run_check("--package", destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unsafe archive output", result.stderr.lower())
                self.assertEqual(destination.read_bytes(), b"preserve this repository file")

    def test_archive_cannot_overwrite_existing_external_file(self):
        destination = Path(self.temp.name) / "existing.zip"
        destination.write_bytes(b"preserve external file")
        result = self.run_check("--package", destination)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("existing external output", result.stderr.lower())
        self.assertEqual(destination.read_bytes(), b"preserve external file")

    def test_dist_archive_can_be_regenerated(self):
        destination = self.root / "dist/dreamie-design.zip"
        first = self.run_check("--package", destination)
        second = self.run_check("--package", destination)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        with zipfile.ZipFile(destination) as archive:
            self.assertIn("dreamie-design/SKILL.md", archive.namelist())

    def test_archive_contains_only_installable_bundle(self):
        (self.root / ".git").mkdir()
        (self.root / ".git/config").write_text("local git config", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests/local.txt").write_text("not runtime content", encoding="utf-8")
        archive = Path(self.temp.name) / "dreamie-design.zip"
        result = self.run_check("--package", archive)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
            self.assertIn("dreamie-design/SKILL.md", names)
            self.assertEqual(len(names), 19)
            self.assertTrue(all(name.startswith("dreamie-design/") for name in names))
            self.assertFalse(any("/.git/" in name or "/tests/" in name for name in names))
            self.assertEqual(
                z.read("dreamie-design/references/layout/methods.md"),
                (self.root / "references/layout/methods.md").read_bytes(),
            )

    def test_invalid_bundle_cannot_create_archive(self):
        (self.root / "references/layout/guide.md").write_text("[Missing](missing.md)", encoding="utf-8")
        archive = Path(self.temp.name) / "bad.zip"
        result = self.run_check("--package", archive)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("broken link", result.stderr.lower())
        self.assertFalse(archive.exists())


if __name__ == "__main__":
    unittest.main()
