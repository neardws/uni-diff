"""Tests for diff engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters import get_converter
from converters.base import ConvertedDocument
from diff import DiffEngine, DiffResult, DiffHunk, DiffType

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestDiffEngine(unittest.TestCase):
    """Tests for DiffEngine."""

    def setUp(self):
        self.engine = DiffEngine(context_lines=3)

    def test_identical_files(self):
        """Test comparing identical files."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        result = self.engine.diff(doc, doc)
        
        self.assertIsInstance(result, DiffResult)
        self.assertEqual(result.similarity_ratio, 1.0)
        self.assertFalse(result.has_changes)

    def test_different_files(self):
        """Test comparing different files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        
        self.assertIsInstance(result, DiffResult)
        self.assertTrue(result.has_changes)
        self.assertLess(result.similarity_ratio, 1.0)
        self.assertGreater(result.similarity_ratio, 0.0)

    def test_diff_stats(self):
        """Test diff statistics."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        
        self.assertIn('insertions', result.stats)
        self.assertIn('deletions', result.stats)
        self.assertIn('modifications', result.stats)
        self.assertIn('unchanged', result.stats)

    def test_diff_hunks(self):
        """Test diff hunks structure."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        
        self.assertTrue(len(result.hunks) > 0)
        for hunk in result.hunks:
            self.assertIsInstance(hunk, DiffHunk)
            self.assertIsInstance(hunk.diff_type, DiffType)

    def test_diff_types(self):
        """Test all diff types are handled."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.py')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.py')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        
        diff_types = {h.diff_type for h in result.hunks}
        self.assertIn(DiffType.EQUAL, diff_types)
        self.assertTrue(
            DiffType.INSERT in diff_types or 
            DiffType.DELETE in diff_types or 
            DiffType.REPLACE in diff_types
        )

    def test_changes_only_property(self):
        """Test changes_only property."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        changes = result.changes_only
        
        for hunk in changes:
            self.assertNotEqual(hunk.diff_type, DiffType.EQUAL)

    def test_unified_diff(self):
        """Test unified diff output."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        unified = self.engine.unified_diff(old_doc, new_doc, 'old.txt', 'new.txt')
        
        self.assertIsInstance(unified, str)
        self.assertIn('---', unified)
        self.assertIn('+++', unified)
        self.assertIn('@@', unified)

    def test_context_diff(self):
        """Test context diff output."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        context = self.engine.context_diff(old_doc, new_doc, 'old.txt', 'new.txt')
        
        self.assertIsInstance(context, str)
        self.assertIn('***', context)

    def test_block_diff(self):
        """Test block-level diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.md')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.md')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff_blocks(old_doc, new_doc)
        
        self.assertIsInstance(result, DiffResult)
        self.assertTrue(result.has_changes)

    def test_diff_result_to_dict(self):
        """Test DiffResult serialization."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        data = result.to_dict()
        
        self.assertIn('similarity_ratio', data)
        self.assertIn('stats', data)
        self.assertIn('hunks', data)

    def test_diff_hunk_to_dict(self):
        """Test DiffHunk serialization."""
        hunk = DiffHunk(
            diff_type=DiffType.REPLACE,
            old_text="old",
            new_text="new",
            old_start=0,
            old_end=1,
            new_start=0,
            new_end=1
        )
        data = hunk.to_dict()
        
        self.assertEqual(data['type'], 'replace')
        self.assertEqual(data['old_text'], 'old')
        self.assertEqual(data['new_text'], 'new')


class TestDiffEngineWithDifferentFileTypes(unittest.TestCase):
    """Test diff engine with various file types."""

    def setUp(self):
        self.engine = DiffEngine()

    def test_json_diff(self):
        """Test diff on JSON files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.json')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.json')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_yaml_diff(self):
        """Test diff on YAML files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.yaml')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.yaml')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_xml_diff(self):
        """Test diff on XML files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.xml')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.xml')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_css_diff(self):
        """Test diff on CSS files."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.css')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.css')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_js_diff(self):
        """Test diff on JavaScript files."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.js')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.js')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_ini_diff(self):
        """Test diff on INI files."""
        old_path = os.path.join(FIXTURES_DIR, 'config', 'old.ini')
        new_path = os.path.join(FIXTURES_DIR, 'config', 'new.ini')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)

    def test_toml_diff(self):
        """Test diff on TOML files."""
        old_path = os.path.join(FIXTURES_DIR, 'config', 'old.toml')
        new_path = os.path.join(FIXTURES_DIR, 'config', 'new.toml')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        result = self.engine.diff(old_doc, new_doc)
        self.assertTrue(result.has_changes)


if __name__ == '__main__':
    unittest.main()
