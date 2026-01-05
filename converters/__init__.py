from .base import BaseConverter, ConvertedDocument, TextBlock
from .pdf import PDFConverter
from .docx import DOCXConverter
from .xlsx import XLSXConverter
from .pptx import PPTXConverter
from .image import ImageConverter
from .text import TextConverter

CONVERTERS = {
    '.pdf': PDFConverter,
    '.docx': DOCXConverter,
    '.xlsx': XLSXConverter,
    '.pptx': PPTXConverter,
    '.png': ImageConverter,
    '.jpg': ImageConverter,
    '.jpeg': ImageConverter,
    '.gif': ImageConverter,
    '.bmp': ImageConverter,
    '.tiff': ImageConverter,
    '.txt': TextConverter,
    '.md': TextConverter,
    '.markdown': TextConverter,
    '.json': TextConverter,
    '.xml': TextConverter,
    '.html': TextConverter,
    '.css': TextConverter,
    '.js': TextConverter,
    '.py': TextConverter,
    '.yaml': TextConverter,
    '.yml': TextConverter,
    '.toml': TextConverter,
    '.ini': TextConverter,
    '.conf': TextConverter,
    '.cfg': TextConverter,
    '.log': TextConverter,
    '.csv': TextConverter,
}

def get_converter(file_path: str) -> BaseConverter:
    """Get appropriate converter based on file extension."""
    import os
    ext = os.path.splitext(file_path)[1].lower()
    converter_class = CONVERTERS.get(ext)
    if converter_class is None:
        converter_class = TextConverter
    return converter_class()

__all__ = [
    'BaseConverter', 'ConvertedDocument', 'TextBlock',
    'PDFConverter', 'DOCXConverter', 'XLSXConverter',
    'PPTXConverter', 'ImageConverter', 'TextConverter',
    'CONVERTERS', 'get_converter'
]
