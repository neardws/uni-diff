from typing import Optional, Union
import os
import sys

from .base import BaseRenderer
from diff.engine import DiffResult, DiffType


class TUIRenderer(BaseRenderer):
    """Render diff results as an interactive TUI using curses."""

    @property
    def output_extension(self) -> str:
        return ''

    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> None:
        if output:
            from .ansi import ANSIRenderer
            ansi = ANSIRenderer()
            content = ansi.render(diff_result)
            with open(output, 'w') as f:
                f.write(content)
            return None

        try:
            import curses
            curses.wrapper(lambda stdscr: self._run_tui(stdscr, diff_result))
        except ImportError:
            from .ansi import ANSIRenderer
            ansi = ANSIRenderer()
            print(ansi.render(diff_result))

    def _run_tui(self, stdscr, diff_result: DiffResult):
        import curses

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)

        curses.curs_set(0)
        stdscr.keypad(True)

        old_lines = diff_result.old_doc.full_text.splitlines() if diff_result.old_doc else []
        new_lines = diff_result.new_doc.full_text.splitlines() if diff_result.new_doc else []

        display_lines = []
        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.old_start, hunk.old_end):
                    if i < len(old_lines):
                        display_lines.append(('equal', old_lines[i], old_lines[i]))
            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_start, hunk.old_end):
                    if i < len(old_lines):
                        display_lines.append(('delete', old_lines[i], ''))
            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_start, hunk.new_end):
                    if i < len(new_lines):
                        display_lines.append(('insert', '', new_lines[i]))
            elif hunk.diff_type == DiffType.REPLACE:
                old_chunk = [old_lines[i] for i in range(hunk.old_start, hunk.old_end) if i < len(old_lines)]
                new_chunk = [new_lines[i] for i in range(hunk.new_start, hunk.new_end) if i < len(new_lines)]
                max_len = max(len(old_chunk), len(new_chunk))
                for i in range(max_len):
                    old_text = old_chunk[i] if i < len(old_chunk) else ''
                    new_text = new_chunk[i] if i < len(new_chunk) else ''
                    display_lines.append(('replace', old_text, new_text))

        scroll_pos = 0
        view_mode = 'split'

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            old_name = os.path.basename(diff_result.old_doc.source_path) if diff_result.old_doc else "Old"
            new_name = os.path.basename(diff_result.new_doc.source_path) if diff_result.new_doc else "New"

            header = f" uni-diff | {diff_result.similarity_ratio:.1%} similar | q:quit j/k:scroll "
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr(0, 0, header.ljust(width)[:width-1])
            stdscr.attroff(curses.color_pair(5))

            if view_mode == 'split':
                panel_width = (width - 1) // 2

                stdscr.attron(curses.A_BOLD | curses.color_pair(1))
                stdscr.addstr(1, 0, f"- {old_name}"[:panel_width-1])
                stdscr.attroff(curses.A_BOLD | curses.color_pair(1))

                stdscr.attron(curses.A_BOLD | curses.color_pair(2))
                stdscr.addstr(1, panel_width + 1, f"+ {new_name}"[:panel_width-1])
                stdscr.attroff(curses.A_BOLD | curses.color_pair(2))

                for y in range(2, height - 1):
                    stdscr.addch(y, panel_width, '|')

                content_height = height - 3
                for i, (dtype, old_text, new_text) in enumerate(display_lines[scroll_pos:scroll_pos + content_height]):
                    y = i + 2
                    if y >= height - 1:
                        break

                    if dtype == 'delete':
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(y, 0, old_text[:panel_width-1])
                        stdscr.attroff(curses.color_pair(1))
                    elif dtype == 'insert':
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(y, panel_width + 1, new_text[:panel_width-1])
                        stdscr.attroff(curses.color_pair(2))
                    elif dtype == 'replace':
                        stdscr.attron(curses.color_pair(3))
                        stdscr.addstr(y, 0, old_text[:panel_width-1])
                        stdscr.attroff(curses.color_pair(3))
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(y, panel_width + 1, new_text[:panel_width-1])
                        stdscr.attroff(curses.color_pair(2))
                    else:
                        stdscr.addstr(y, 0, old_text[:panel_width-1])
                        stdscr.addstr(y, panel_width + 1, new_text[:panel_width-1])

            else:
                content_height = height - 3
                for i, (dtype, old_text, new_text) in enumerate(display_lines[scroll_pos:scroll_pos + content_height]):
                    y = i + 2
                    if y >= height - 1:
                        break

                    if dtype == 'delete':
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(y, 0, f"- {old_text}"[:width-1])
                        stdscr.attroff(curses.color_pair(1))
                    elif dtype == 'insert':
                        stdscr.attron(curses.color_pair(2))
                        stdscr.addstr(y, 0, f"+ {new_text}"[:width-1])
                        stdscr.attroff(curses.color_pair(2))
                    elif dtype == 'replace':
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(y, 0, f"- {old_text}"[:width-1])
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(y, 0, f"  {old_text}"[:width-1])

            stats = diff_result.stats
            footer = f" +{stats.get('insertions', 0)} -{stats.get('deletions', 0)} ~{stats.get('modifications', 0)} | Line {scroll_pos + 1}/{len(display_lines)} | v:toggle view "
            stdscr.attron(curses.color_pair(5))
            stdscr.addstr(height - 1, 0, footer.ljust(width)[:width-1])
            stdscr.attroff(curses.color_pair(5))

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('j') or key == curses.KEY_DOWN:
                if scroll_pos < len(display_lines) - 1:
                    scroll_pos += 1
            elif key == ord('k') or key == curses.KEY_UP:
                if scroll_pos > 0:
                    scroll_pos -= 1
            elif key == ord('d') or key == curses.KEY_NPAGE:
                scroll_pos = min(scroll_pos + (height - 3), len(display_lines) - 1)
            elif key == ord('u') or key == curses.KEY_PPAGE:
                scroll_pos = max(scroll_pos - (height - 3), 0)
            elif key == ord('g') or key == curses.KEY_HOME:
                scroll_pos = 0
            elif key == ord('G') or key == curses.KEY_END:
                scroll_pos = max(0, len(display_lines) - (height - 3))
            elif key == ord('v'):
                view_mode = 'unified' if view_mode == 'split' else 'split'
