"""Tests for diff renderers."""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters import get_converter
from diff import DiffEngine
from renderers import get_renderer, RENDERERS
from renderers.base import BaseRenderer

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def get_sample_diff():
    """Get a sample diff result for testing."""
    old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
    new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
    
    old_doc = get_converter(old_path).convert(old_path)
    new_doc = get_converter(new_path).convert(new_path)
    
    engine = DiffEngine()
    return engine.diff(old_doc, new_doc)


class TestRendererRegistry(unittest.TestCase):
    """Tests for renderer registry."""

    def test_available_renderers(self):
        """Test that all expected renderers are available."""
        expected = {'png', 'html', 'json', 'tui', 'ansi', 'terminal'}
        self.assertEqual(set(RENDERERS.keys()), expected)

    def test_get_renderer(self):
        """Test get_renderer function."""
        renderer = get_renderer('json')
        self.assertIsInstance(renderer, BaseRenderer)

    def test_get_renderer_case_insensitive(self):
        """Test get_renderer is case insensitive."""
        renderer1 = get_renderer('JSON')
        renderer2 = get_renderer('json')
        self.assertEqual(type(renderer1), type(renderer2))

    def test_get_renderer_invalid(self):
        """Test get_renderer with invalid format."""
        with self.assertRaises(ValueError):
            get_renderer('invalid_format')


class TestJSONRenderer(unittest.TestCase):
    """Tests for JSON renderer."""

    def test_json_render(self):
        """Test JSON rendering."""
        diff_result = get_sample_diff()
        renderer = get_renderer('json')
        
        output = renderer.render(diff_result)
        
        self.assertIsInstance(output, str)
        data = json.loads(output)
        self.assertIn('summary', data)
        self.assertIn('similarity_ratio', data['summary'])
        self.assertIn('hunks', data)

    def test_json_structure(self):
        """Test JSON output structure."""
        diff_result = get_sample_diff()
        renderer = get_renderer('json')
        
        output = renderer.render(diff_result)
        data = json.loads(output)
        
        self.assertIsInstance(data['summary']['similarity_ratio'], float)
        self.assertIsInstance(data['summary']['stats'], dict)
        self.assertIsInstance(data['hunks'], list)

    def test_json_hunks_structure(self):
        """Test JSON hunks structure."""
        diff_result = get_sample_diff()
        renderer = get_renderer('json')
        
        output = renderer.render(diff_result)
        data = json.loads(output)
        
        for hunk in data['hunks']:
            self.assertIn('type', hunk)
            self.assertIn('old_text', hunk)
            self.assertIn('new_text', hunk)


class TestANSIRenderer(unittest.TestCase):
    """Tests for ANSI renderer."""

    def test_ansi_render(self):
        """Test ANSI rendering."""
        diff_result = get_sample_diff()
        renderer = get_renderer('ansi')
        
        output = renderer.render(diff_result)
        
        self.assertIsInstance(output, str)
        self.assertTrue(len(output) > 0)

    def test_ansi_contains_diff_markers(self):
        """Test ANSI output contains diff markers."""
        diff_result = get_sample_diff()
        renderer = get_renderer('ansi')
        
        output = renderer.render(diff_result)
        
        self.assertTrue(
            '@@' in output or 
            '---' in output or 
            '+++' in output or
            '-' in output or
            '+' in output
        )

    def test_terminal_alias(self):
        """Test 'terminal' alias works."""
        diff_result = get_sample_diff()
        renderer = get_renderer('terminal')
        
        output = renderer.render(diff_result)
        self.assertIsInstance(output, str)


class TestHTMLRenderer(unittest.TestCase):
    """Tests for HTML renderer."""

    def test_html_render(self):
        """Test HTML rendering."""
        diff_result = get_sample_diff()
        renderer = get_renderer('html')
        
        output = renderer.render(diff_result)
        
        self.assertIsInstance(output, str)
        self.assertIn('<!DOCTYPE html>', output)
        self.assertIn('<html', output)
        self.assertIn('</html>', output)

    def test_html_contains_diff_content(self):
        """Test HTML contains diff content."""
        diff_result = get_sample_diff()
        renderer = get_renderer('html')
        
        output = renderer.render(diff_result)
        
        self.assertIn('class=', output)
        self.assertIn('<div', output)

    def test_html_file_output(self):
        """Test HTML output to file."""
        import tempfile
        
        diff_result = get_sample_diff()
        renderer = get_renderer('html')
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            renderer.render(diff_result, output_path)
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestPNGRenderer(unittest.TestCase):
    """Tests for PNG renderer."""

    def test_png_renderer_available(self):
        """Test PNG renderer is available."""
        renderer = get_renderer('png')
        self.assertIsNotNone(renderer)

    def test_png_render(self):
        """Test PNG rendering."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        
        diff_result = get_sample_diff()
        renderer = get_renderer('png')
        
        output = renderer.render(diff_result)
        
        self.assertIsInstance(output, bytes)

    def test_png_file_output(self):
        """Test PNG output to file."""
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        
        import tempfile
        
        diff_result = get_sample_diff()
        renderer = get_renderer('png')
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            output_path = f.name
        
        try:
            renderer.render(diff_result, output_path)
            self.assertTrue(os.path.exists(output_path))
            
            img = Image.open(output_path)
            self.assertIsNotNone(img.size)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestTUIRenderer(unittest.TestCase):
    """Tests for TUI renderer."""

    def test_tui_renderer_available(self):
        """Test TUI renderer is available."""
        renderer = get_renderer('tui')
        self.assertIsNotNone(renderer)


class TestRendererWithDifferentDiffs(unittest.TestCase):
    """Test renderers with different diff types."""

    def test_json_with_code_diff(self):
        """Test JSON renderer with code diff."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.py')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.py')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        engine = DiffEngine()
        diff_result = engine.diff(old_doc, new_doc)
        
        renderer = get_renderer('json')
        output = renderer.render(diff_result)
        
        data = json.loads(output)
        self.assertTrue(len(data['hunks']) > 0)

    def test_ansi_with_config_diff(self):
        """Test ANSI renderer with config diff."""
        old_path = os.path.join(FIXTURES_DIR, 'config', 'old.ini')
        new_path = os.path.join(FIXTURES_DIR, 'config', 'new.ini')
        
        old_doc = get_converter(old_path).convert(old_path)
        new_doc = get_converter(new_path).convert(new_path)
        
        engine = DiffEngine()
        diff_result = engine.diff(old_doc, new_doc)
        
        renderer = get_renderer('ansi')
        output = renderer.render(diff_result)
        
        self.assertIsInstance(output, str)


if __name__ == '__main__':
    unittest.main()
