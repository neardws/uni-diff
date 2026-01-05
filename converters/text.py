import os
from typing import List
from .base import BaseConverter, ConvertedDocument, TextBlock


class TextConverter(BaseConverter):
    """Converter for plain text files."""

    @property
    def supported_extensions(self) -> List[str]:
        return [
            '.txt', '.md', '.markdown', '.rst',
            '.json', '.xml', '.html', '.css', '.js',
            '.py', '.java', '.c', '.cpp', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.sh', '.bash',
            '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg',
            '.log', '.csv', '.tsv'
        ]

    def convert(self, file_path: str) -> ConvertedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii']
        full_text = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    full_text = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if full_text is None:
            with open(file_path, 'rb') as f:
                raw = f.read()
            full_text = raw.decode('utf-8', errors='replace')

        blocks = []
        lines = full_text.split('\n')

        y_offset = 0
        for i, line in enumerate(lines):
            blocks.append(TextBlock(
                text=line,
                page=0,
                x=0,
                y=y_offset,
                width=len(line) * 7,
                height=12,
                metadata={'line_number': i + 1}
            ))
            y_offset += 12

        ext = os.path.splitext(file_path)[1].lower()

        return ConvertedDocument(
            blocks=blocks,
            full_text=full_text,
            page_count=1,
            metadata={
                'line_count': len(lines),
                'char_count': len(full_text),
                'extension': ext
            },
            source_path=file_path,
            source_type='text'
        )
