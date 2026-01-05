"""Tests for document converters."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converters import get_converter, TextConverter
from converters.base import ConvertedDocument, TextBlock

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestTextConverter(unittest.TestCase):
    """Tests for TextConverter."""

    def test_txt_conversion(self):
        """Test plain text file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        converter = get_converter(path)
        self.assertIsInstance(converter, TextConverter)
        
        doc = converter.convert(path)
        self.assertIsInstance(doc, ConvertedDocument)
        self.assertTrue(len(doc.full_text) > 0)
        self.assertTrue(len(doc.blocks) > 0)
        self.assertEqual(doc.source_type, 'text')

    def test_md_conversion(self):
        """Test Markdown file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.md')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('# Document Title', doc.full_text)
        self.assertTrue(any('Introduction' in b.text for b in doc.blocks))

    def test_json_conversion(self):
        """Test JSON file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.json')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('"name"', doc.full_text)
        self.assertIn('test-project', doc.full_text)

    def test_xml_conversion(self):
        """Test XML file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.xml')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('<?xml', doc.full_text)
        self.assertIn('<root>', doc.full_text)

    def test_yaml_conversion(self):
        """Test YAML file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.yaml')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('name: my-app', doc.full_text)

    def test_csv_conversion(self):
        """Test CSV file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.csv')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('id,name,email,score', doc.full_text)

    def test_html_conversion(self):
        """Test HTML file conversion."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.html')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('<!DOCTYPE html>', doc.full_text)
        self.assertIn('<title>Test Page</title>', doc.full_text)

    def test_py_conversion(self):
        """Test Python file conversion."""
        path = os.path.join(FIXTURES_DIR, 'code', 'old.py')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('def greet(name):', doc.full_text)
        self.assertIn('class Calculator:', doc.full_text)

    def test_js_conversion(self):
        """Test JavaScript file conversion."""
        path = os.path.join(FIXTURES_DIR, 'code', 'old.js')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('function add(a, b)', doc.full_text)

    def test_css_conversion(self):
        """Test CSS file conversion."""
        path = os.path.join(FIXTURES_DIR, 'code', 'old.css')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('.container', doc.full_text)
        self.assertIn('font-family', doc.full_text)

    def test_ini_conversion(self):
        """Test INI file conversion."""
        path = os.path.join(FIXTURES_DIR, 'config', 'old.ini')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('[general]', doc.full_text)
        self.assertIn('[database]', doc.full_text)

    def test_toml_conversion(self):
        """Test TOML file conversion."""
        path = os.path.join(FIXTURES_DIR, 'config', 'old.toml')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        self.assertIn('[package]', doc.full_text)
        self.assertIn('[dependencies]', doc.full_text)

    def test_block_metadata(self):
        """Test that blocks have proper metadata."""
        path = os.path.join(FIXTURES_DIR, 'text', 'old.txt')
        converter = get_converter(path)
        doc = converter.convert(path)
        
        for block in doc.blocks:
            self.assertIsInstance(block, TextBlock)
            self.assertIn('line_number', block.metadata)
            self.assertIsInstance(block.metadata['line_number'], int)

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        converter = TextConverter()
        with self.assertRaises(FileNotFoundError):
            converter.convert('/nonexistent/file.txt')


class TestOfficeConverters(unittest.TestCase):
    """Tests for Office document converters (optional)."""

    def test_docx_converter_available(self):
        """Test if DOCX converter is available."""
        from converters import DOCXConverter
        converter = DOCXConverter()
        self.assertIn('.docx', converter.supported_extensions)

    def test_xlsx_converter_available(self):
        """Test if XLSX converter is available."""
        from converters import XLSXConverter
        converter = XLSXConverter()
        self.assertIn('.xlsx', converter.supported_extensions)

    def test_pptx_converter_available(self):
        """Test if PPTX converter is available."""
        from converters import PPTXConverter
        converter = PPTXConverter()
        self.assertIn('.pptx', converter.supported_extensions)

    def test_docx_conversion(self):
        """Test Word document conversion."""
        path = os.path.join(FIXTURES_DIR, 'office', 'old.docx')
        if not os.path.exists(path):
            self.skipTest("DOCX fixture not generated")
        
        try:
            from converters import DOCXConverter
            converter = DOCXConverter()
            doc = converter.convert(path)
            self.assertIsInstance(doc, ConvertedDocument)
            self.assertTrue(len(doc.full_text) > 0)
        except ImportError:
            self.skipTest("python-docx not installed")

    def test_xlsx_conversion(self):
        """Test Excel file conversion."""
        path = os.path.join(FIXTURES_DIR, 'office', 'old.xlsx')
        if not os.path.exists(path):
            self.skipTest("XLSX fixture not generated")
        
        try:
            from converters import XLSXConverter
            converter = XLSXConverter()
            doc = converter.convert(path)
            self.assertIsInstance(doc, ConvertedDocument)
            self.assertTrue(len(doc.full_text) > 0)
        except ImportError:
            self.skipTest("openpyxl not installed")

    def test_pptx_conversion(self):
        """Test PowerPoint file conversion."""
        path = os.path.join(FIXTURES_DIR, 'office', 'old.pptx')
        if not os.path.exists(path):
            self.skipTest("PPTX fixture not generated")
        
        try:
            from converters import PPTXConverter
            converter = PPTXConverter()
            doc = converter.convert(path)
            self.assertIsInstance(doc, ConvertedDocument)
            self.assertTrue(len(doc.full_text) > 0)
        except ImportError:
            self.skipTest("python-pptx not installed")


class TestPDFConverter(unittest.TestCase):
    """Tests for PDF converter (optional)."""

    def test_pdf_conversion(self):
        """Test PDF file conversion."""
        path = os.path.join(FIXTURES_DIR, 'pdf', 'old.pdf')
        if not os.path.exists(path):
            self.skipTest("PDF fixture not generated")
        
        try:
            from converters import PDFConverter
            converter = PDFConverter()
            doc = converter.convert(path)
            self.assertIsInstance(doc, ConvertedDocument)
        except (ImportError, RuntimeError) as e:
            self.skipTest(f"PDF converter not available: {e}")


class TestImageConverter(unittest.TestCase):
    """Tests for image converter (optional)."""

    def test_image_conversion(self):
        """Test image file conversion."""
        path = os.path.join(FIXTURES_DIR, 'images', 'old.png')
        if not os.path.exists(path):
            self.skipTest("Image fixture not generated")
        
        try:
            from converters import ImageConverter
            converter = ImageConverter()
            doc = converter.convert(path)
            self.assertIsInstance(doc, ConvertedDocument)
        except (ImportError, RuntimeError) as e:
            self.skipTest(f"Image converter not available: {e}")


if __name__ == '__main__':
    unittest.main()
