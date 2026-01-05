"""Tests for CLI interface."""

import os
import sys
import json
import subprocess
import tempfile
import unittest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(PROJECT_DIR, 'cli.py')


class TestCLIBasic(unittest.TestCase):
    """Basic CLI tests."""

    def run_cli(self, args, check=False):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        if check and result.returncode not in (0, 1):
            print(f"STDERR: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return result

    def test_version(self):
        """Test --version flag."""
        result = self.run_cli(['--version'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('uni-diff', result.stdout)

    def test_help(self):
        """Test --help flag."""
        result = self.run_cli(['--help'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())
        self.assertIn('old_file', result.stdout)
        self.assertIn('new_file', result.stdout)

    def test_missing_args(self):
        """Test CLI with missing arguments."""
        result = self.run_cli([])
        self.assertNotEqual(result.returncode, 0)

    def test_file_not_found(self):
        """Test CLI with non-existent file."""
        result = self.run_cli(['/nonexistent/old.txt', '/nonexistent/new.txt'])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Error', result.stderr)


class TestCLITextFiles(unittest.TestCase):
    """CLI tests with text files."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_txt_diff_ansi(self):
        """Test text file diff with ANSI output."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        result = self.run_cli([old_path, new_path, '-f', 'ansi'])
        
        self.assertIn(result.returncode, (0, 1))
        self.assertTrue(len(result.stdout) > 0 or len(result.stderr) > 0)

    def test_txt_diff_json(self):
        """Test text file diff with JSON output."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))
        data = json.loads(result.stdout)
        self.assertIn('summary', data)
        self.assertIn('similarity_ratio', data['summary'])

    def test_md_diff_json(self):
        """Test Markdown file diff with JSON output."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.md')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.md')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))
        data = json.loads(result.stdout)
        self.assertTrue(len(data['hunks']) > 0)

    def test_json_diff(self):
        """Test JSON file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.json')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.json')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_yaml_diff(self):
        """Test YAML file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.yaml')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.yaml')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_xml_diff(self):
        """Test XML file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.xml')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.xml')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_csv_diff(self):
        """Test CSV file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.csv')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.csv')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_html_diff(self):
        """Test HTML file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.html')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.html')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))


class TestCLICodeFiles(unittest.TestCase):
    """CLI tests with code files."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_py_diff(self):
        """Test Python file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.py')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.py')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))
        data = json.loads(result.stdout)
        self.assertLess(data['summary']['similarity_ratio'], 1.0)

    def test_js_diff(self):
        """Test JavaScript file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.js')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.js')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_css_diff(self):
        """Test CSS file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'code', 'old.css')
        new_path = os.path.join(FIXTURES_DIR, 'code', 'new.css')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))


class TestCLIConfigFiles(unittest.TestCase):
    """CLI tests with config files."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_ini_diff(self):
        """Test INI file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'config', 'old.ini')
        new_path = os.path.join(FIXTURES_DIR, 'config', 'new.ini')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_toml_diff(self):
        """Test TOML file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'config', 'old.toml')
        new_path = os.path.join(FIXTURES_DIR, 'config', 'new.toml')
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))


class TestCLIOptions(unittest.TestCase):
    """CLI options tests."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_summary_option(self):
        """Test --summary option."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        result = self.run_cli([old_path, new_path, '--summary'])
        
        self.assertIn(result.returncode, (0, 1))
        self.assertIn('Similarity:', result.stdout)
        self.assertIn('Insertions:', result.stdout)
        self.assertIn('Deletions:', result.stdout)

    def test_quiet_option_with_changes(self):
        """Test --quiet option with changed files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        result = self.run_cli([old_path, new_path, '-q', '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_quiet_option_identical(self):
        """Test --quiet option with identical files."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        
        result = self.run_cli([old_path, old_path, '-q'])
        
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '')

    def test_context_option(self):
        """Test --context option."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        result = self.run_cli([old_path, new_path, '-c', '5', '-f', 'ansi'])
        
        self.assertIn(result.returncode, (0, 1))

    def test_output_to_file(self):
        """Test output to file."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.txt')
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            result = self.run_cli([old_path, new_path, '-f', 'html', '-o', output_path])
            
            self.assertIn(result.returncode, (0, 1))
            self.assertTrue(os.path.exists(output_path))
            
            with open(output_path, 'r') as f:
                content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_block_diff_option(self):
        """Test --block-diff option."""
        old_path = os.path.join(FIXTURES_DIR, 'text', 'old.md')
        new_path = os.path.join(FIXTURES_DIR, 'text', 'new.md')
        
        result = self.run_cli([old_path, new_path, '--block-diff', '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1))


class TestCLIOfficeFiles(unittest.TestCase):
    """CLI tests with Office files (optional)."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_docx_diff(self):
        """Test Word document diff."""
        old_path = os.path.join(FIXTURES_DIR, 'office', 'old.docx')
        new_path = os.path.join(FIXTURES_DIR, 'office', 'new.docx')
        
        if not os.path.exists(old_path):
            self.skipTest("DOCX fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        if 'Error' in result.stderr and 'not installed' in result.stderr.lower():
            self.skipTest("python-docx not installed")
        
        self.assertIn(result.returncode, (0, 1, 2))

    def test_xlsx_diff(self):
        """Test Excel file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'office', 'old.xlsx')
        new_path = os.path.join(FIXTURES_DIR, 'office', 'new.xlsx')
        
        if not os.path.exists(old_path):
            self.skipTest("XLSX fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1, 2))

    def test_pptx_diff(self):
        """Test PowerPoint file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'office', 'old.pptx')
        new_path = os.path.join(FIXTURES_DIR, 'office', 'new.pptx')
        
        if not os.path.exists(old_path):
            self.skipTest("PPTX fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1, 2))


class TestCLIPDFFiles(unittest.TestCase):
    """CLI tests with PDF files (optional)."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_pdf_diff(self):
        """Test PDF file diff."""
        old_path = os.path.join(FIXTURES_DIR, 'pdf', 'old.pdf')
        new_path = os.path.join(FIXTURES_DIR, 'pdf', 'new.pdf')
        
        if not os.path.exists(old_path):
            self.skipTest("PDF fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1, 2))


class TestCLIImageFiles(unittest.TestCase):
    """CLI tests with image files (optional)."""

    def run_cli(self, args):
        """Run CLI command and return result."""
        cmd = [sys.executable, CLI_PATH] + args
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

    def test_png_diff(self):
        """Test PNG image diff."""
        old_path = os.path.join(FIXTURES_DIR, 'images', 'old.png')
        new_path = os.path.join(FIXTURES_DIR, 'images', 'new.png')
        
        if not os.path.exists(old_path):
            self.skipTest("PNG fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1, 2))

    def test_jpg_diff(self):
        """Test JPEG image diff."""
        old_path = os.path.join(FIXTURES_DIR, 'images', 'old.jpg')
        new_path = os.path.join(FIXTURES_DIR, 'images', 'new.jpg')
        
        if not os.path.exists(old_path):
            self.skipTest("JPG fixtures not generated")
        
        result = self.run_cli([old_path, new_path, '-f', 'json'])
        
        self.assertIn(result.returncode, (0, 1, 2))


if __name__ == '__main__':
    unittest.main()
