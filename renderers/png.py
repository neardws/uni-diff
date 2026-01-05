from typing import Optional, Union
import os

from .base import BaseRenderer
from diff.engine import DiffResult, DiffType


class PNGRenderer(BaseRenderer):
    """Render diff results as PNG images with visual annotations."""

    def __init__(self, scale: float = 2.0, margin: int = 20):
        self.scale = scale
        self.margin = margin

    @property
    def output_extension(self) -> str:
        return '.png'

    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> Union[bytes, None]:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise RuntimeError("Pillow is required for PNG output. Install: pip install Pillow")

        line_height = int(14 * self.scale)
        char_width = int(7 * self.scale)
        font_size = int(12 * self.scale)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("Courier", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        old_lines = diff_result.old_doc.full_text.splitlines() if diff_result.old_doc else []
        new_lines = diff_result.new_doc.full_text.splitlines() if diff_result.new_doc else []

        max_old_len = max((len(line) for line in old_lines), default=0)
        max_new_len = max((len(line) for line in new_lines), default=0)

        panel_width = max(max_old_len, max_new_len, 40) * char_width + self.margin * 2
        total_width = panel_width * 2 + self.margin * 3

        max_lines = max(len(old_lines), len(new_lines))
        header_height = int(30 * self.scale)
        total_height = header_height + max_lines * line_height + self.margin * 2

        img = Image.new('RGB', (total_width, total_height), color='white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, total_width, header_height], fill='#f0f0f0')

        old_label = os.path.basename(diff_result.old_doc.source_path) if diff_result.old_doc else "Old"
        new_label = os.path.basename(diff_result.new_doc.source_path) if diff_result.new_doc else "New"

        draw.text((self.margin, 5), f"- {old_label}", fill='#c00000', font=font)
        draw.text((panel_width + self.margin * 2, 5), f"+ {new_label}", fill='#00c000', font=font)

        draw.line([(panel_width + self.margin, 0), (panel_width + self.margin, total_height)], fill='#cccccc', width=2)

        old_line_idx = 0
        new_line_idx = 0

        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_line_idx < len(old_lines):
                        y = header_height + old_line_idx * line_height
                        draw.text((self.margin, y), old_lines[old_line_idx], fill='black', font=font)
                        old_line_idx += 1
                    if new_line_idx < len(new_lines):
                        y = header_height + new_line_idx * line_height
                        draw.text((panel_width + self.margin * 2, y), new_lines[new_line_idx], fill='black', font=font)
                        new_line_idx += 1

            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_line_idx < len(old_lines):
                        y = header_height + old_line_idx * line_height
                        text_width = len(old_lines[old_line_idx]) * char_width
                        draw.rectangle(
                            [self.margin - 2, y, self.margin + text_width + 2, y + line_height],
                            fill='#ffcccc',
                            outline='#ff0000',
                            width=1
                        )
                        draw.text((self.margin, y), old_lines[old_line_idx], fill='#800000', font=font)
                        old_line_idx += 1

            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_end - hunk.new_start):
                    if new_line_idx < len(new_lines):
                        y = header_height + new_line_idx * line_height
                        text_width = len(new_lines[new_line_idx]) * char_width
                        draw.rectangle(
                            [panel_width + self.margin * 2 - 2, y,
                             panel_width + self.margin * 2 + text_width + 2, y + line_height],
                            fill='#ccffcc',
                            outline='#00ff00',
                            width=1
                        )
                        draw.text((panel_width + self.margin * 2, y), new_lines[new_line_idx], fill='#008000', font=font)
                        new_line_idx += 1

            elif hunk.diff_type == DiffType.REPLACE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_line_idx < len(old_lines):
                        y = header_height + old_line_idx * line_height
                        text_width = len(old_lines[old_line_idx]) * char_width
                        draw.rectangle(
                            [self.margin - 2, y, self.margin + text_width + 2, y + line_height],
                            fill='#ffffcc',
                            outline='#ff8800',
                            width=1
                        )
                        draw.text((self.margin, y), old_lines[old_line_idx], fill='#804000', font=font)
                        old_line_idx += 1

                for i in range(hunk.new_end - hunk.new_start):
                    if new_line_idx < len(new_lines):
                        y = header_height + new_line_idx * line_height
                        text_width = len(new_lines[new_line_idx]) * char_width
                        draw.rectangle(
                            [panel_width + self.margin * 2 - 2, y,
                             panel_width + self.margin * 2 + text_width + 2, y + line_height],
                            fill='#ccffcc',
                            outline='#00ff00',
                            width=1
                        )
                        draw.text((panel_width + self.margin * 2, y), new_lines[new_line_idx], fill='#008000', font=font)
                        new_line_idx += 1

        stats = diff_result.stats
        stats_text = f"Similarity: {diff_result.similarity_ratio:.1%} | +{stats.get('insertions', 0)} -{stats.get('deletions', 0)} ~{stats.get('modifications', 0)}"
        draw.rectangle([0, total_height - 25, total_width, total_height], fill='#f0f0f0')
        draw.text((self.margin, total_height - 22), stats_text, fill='#666666', font=font)

        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()

        if output:
            with open(output, 'wb') as f:
                f.write(png_bytes)
            return None
        return png_bytes
