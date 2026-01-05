from typing import Optional, Union
import os

from .base import BaseRenderer
from diff.engine import DiffResult, DiffType


class ANSIRenderer(BaseRenderer):
    """Render diff results with ANSI color codes for terminal output."""

    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

    def __init__(self, color: bool = True, context_lines: int = 3):
        self.color = color
        self.context_lines = context_lines

    @property
    def output_extension(self) -> str:
        return '.txt'

    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> Union[str, None]:
        lines = []

        old_name = os.path.basename(diff_result.old_doc.source_path) if diff_result.old_doc else "old"
        new_name = os.path.basename(diff_result.new_doc.source_path) if diff_result.new_doc else "new"

        lines.append(self._header(diff_result, old_name, new_name))
        lines.append("")

        old_lines = diff_result.old_doc.full_text.splitlines() if diff_result.old_doc else []
        new_lines = diff_result.new_doc.full_text.splitlines() if diff_result.new_doc else []

        old_idx = 0
        new_idx = 0

        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._format_line(' ', old_lines[old_idx], old_idx + 1))
                        old_idx += 1
                        new_idx += 1

            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._format_delete(old_lines[old_idx], old_idx + 1))
                        old_idx += 1

            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_end - hunk.new_start):
                    if new_idx < len(new_lines):
                        lines.append(self._format_insert(new_lines[new_idx], new_idx + 1))
                        new_idx += 1

            elif hunk.diff_type == DiffType.REPLACE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._format_delete(old_lines[old_idx], old_idx + 1))
                        old_idx += 1
                for i in range(hunk.new_end - hunk.new_start):
                    if new_idx < len(new_lines):
                        lines.append(self._format_insert(new_lines[new_idx], new_idx + 1))
                        new_idx += 1

        lines.append("")
        lines.append(self._footer(diff_result))

        content = '\n'.join(lines)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(self._strip_ansi(content) if not self.color else content)
            return None
        return content

    def _header(self, diff_result: DiffResult, old_name: str, new_name: str) -> str:
        if self.color:
            header = f"{self.BOLD}{self.CYAN}━━━ uni-diff ━━━{self.RESET}\n"
            header += f"{self.RED}--- {old_name}{self.RESET}\n"
            header += f"{self.GREEN}+++ {new_name}{self.RESET}"
        else:
            header = f"━━━ uni-diff ━━━\n"
            header += f"--- {old_name}\n"
            header += f"+++ {new_name}"
        return header

    def _footer(self, diff_result: DiffResult) -> str:
        stats = diff_result.stats
        if self.color:
            return (
                f"{self.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{self.RESET}\n"
                f"Similarity: {self.CYAN}{diff_result.similarity_ratio:.1%}{self.RESET} | "
                f"{self.GREEN}+{stats.get('insertions', 0)}{self.RESET} "
                f"{self.RED}-{stats.get('deletions', 0)}{self.RESET} "
                f"{self.YELLOW}~{stats.get('modifications', 0)}{self.RESET}"
            )
        else:
            return (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Similarity: {diff_result.similarity_ratio:.1%} | "
                f"+{stats.get('insertions', 0)} "
                f"-{stats.get('deletions', 0)} "
                f"~{stats.get('modifications', 0)}"
            )

    def _format_line(self, prefix: str, text: str, line_num: int) -> str:
        if self.color:
            return f"{self.DIM}{line_num:4d}{self.RESET} {prefix} {text}"
        return f"{line_num:4d} {prefix} {text}"

    def _format_delete(self, text: str, line_num: int) -> str:
        if self.color:
            return f"{self.RED}{line_num:4d} - {text}{self.RESET}"
        return f"{line_num:4d} - {text}"

    def _format_insert(self, text: str, line_num: int) -> str:
        if self.color:
            return f"{self.GREEN}{line_num:4d} + {text}{self.RESET}"
        return f"{line_num:4d} + {text}"

    def _strip_ansi(self, text: str) -> str:
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
