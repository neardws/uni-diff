"""
uni-diff: Universal file diff tool

Compare any files - PDF, DOCX, XLSX, PPTX, images, and text files.
Output in multiple formats: PNG, HTML, JSON, TUI, or colored terminal.
"""

__version__ = '0.1.0'
__author__ = 'uni-diff contributors'

from converters import get_converter, ConvertedDocument
from diff import DiffEngine, DiffResult
from renderers import get_renderer

__all__ = [
    'get_converter', 'ConvertedDocument',
    'DiffEngine', 'DiffResult',
    'get_renderer',
    '__version__'
]
