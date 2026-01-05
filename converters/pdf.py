import subprocess
import os
from typing import List
from .base import BaseConverter, ConvertedDocument, TextBlock


class PDFConverter(BaseConverter):
    """Converter for PDF files using pdftotext."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.pdf']

    def convert(self, file_path: str) -> ConvertedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        blocks = []
        full_text = ""

        try:
            result = subprocess.run(
                ['pdftotext', '-layout', file_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            full_text = result.stdout

            page_result = subprocess.run(
                ['pdfinfo', file_path],
                capture_output=True,
                text=True
            )
            page_count = 1
            for line in page_result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    page_count = int(line.split(':')[1].strip())
                    break

            lines = full_text.split('\n')
            current_page = 0
            page_marker = '\x0c'

            y_offset = 0
            for line in lines:
                if page_marker in line:
                    current_page += 1
                    y_offset = 0
                    line = line.replace(page_marker, '')

                if line.strip():
                    blocks.append(TextBlock(
                        text=line,
                        page=current_page,
                        x=0,
                        y=y_offset,
                        width=len(line) * 7,
                        height=12
                    ))
                y_offset += 12

        except FileNotFoundError:
            try:
                import pymupdf
                doc = pymupdf.open(file_path)
                page_count = len(doc)
                
                for page_num, page in enumerate(doc):
                    text = page.get_text()
                    full_text += text + "\n"
                    
                    text_dict = page.get_text("dict")
                    for block in text_dict.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                line_text = ""
                                for span in line.get("spans", []):
                                    line_text += span.get("text", "")
                                if line_text.strip():
                                    bbox = block.get("bbox", [0, 0, 0, 0])
                                    blocks.append(TextBlock(
                                        text=line_text,
                                        page=page_num,
                                        x=bbox[0],
                                        y=bbox[1],
                                        width=bbox[2] - bbox[0],
                                        height=bbox[3] - bbox[1]
                                    ))
                doc.close()
            except ImportError:
                raise RuntimeError(
                    "Neither pdftotext nor pymupdf is available. "
                    "Install poppler-utils or pymupdf."
                )

        return ConvertedDocument(
            blocks=blocks,
            full_text=full_text,
            page_count=page_count,
            source_path=file_path,
            source_type='pdf'
        )
