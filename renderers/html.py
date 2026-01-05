from typing import Optional, Union
import html
import os

from .base import BaseRenderer
from diff.engine import DiffResult, DiffType


class HTMLRenderer(BaseRenderer):
    """Render diff results as interactive HTML."""

    @property
    def output_extension(self) -> str:
        return '.html'

    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> Union[str, None]:
        old_name = os.path.basename(diff_result.old_doc.source_path) if diff_result.old_doc else "Old"
        new_name = os.path.basename(diff_result.new_doc.source_path) if diff_result.new_doc else "New"

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diff: {html.escape(old_name)} vs {html.escape(new_name)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace; background: #1e1e1e; color: #d4d4d4; }}
        .header {{ background: #252526; padding: 12px 20px; border-bottom: 1px solid #404040; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 16px; font-weight: 500; }}
        .stats {{ font-size: 13px; color: #808080; }}
        .stats .add {{ color: #4ec9b0; }}
        .stats .del {{ color: #f14c4c; }}
        .stats .mod {{ color: #dcdcaa; }}
        .container {{ display: flex; height: calc(100vh - 50px); }}
        .panel {{ flex: 1; overflow: auto; border-right: 1px solid #404040; }}
        .panel:last-child {{ border-right: none; }}
        .panel-header {{ background: #2d2d2d; padding: 8px 12px; font-size: 12px; color: #808080; position: sticky; top: 0; z-index: 10; }}
        .panel-header.old {{ color: #f14c4c; }}
        .panel-header.new {{ color: #4ec9b0; }}
        .content {{ padding: 0; }}
        .line {{ display: flex; min-height: 20px; font-size: 13px; line-height: 20px; }}
        .line-num {{ width: 50px; text-align: right; padding: 0 8px; color: #606060; background: #1e1e1e; user-select: none; flex-shrink: 0; }}
        .line-text {{ flex: 1; padding: 0 12px; white-space: pre-wrap; word-break: break-all; }}
        .line.equal {{ background: transparent; }}
        .line.delete {{ background: rgba(244, 67, 54, 0.15); }}
        .line.delete .line-text {{ color: #f14c4c; }}
        .line.insert {{ background: rgba(76, 175, 80, 0.15); }}
        .line.insert .line-text {{ color: #4ec9b0; }}
        .line.modify {{ background: rgba(255, 193, 7, 0.15); }}
        .line.modify .line-text {{ color: #dcdcaa; }}
        .line.empty {{ background: #262626; }}
        .line.empty .line-text {{ color: #404040; }}
        .view-toggle {{ display: flex; gap: 8px; }}
        .view-toggle button {{ background: #404040; border: none; color: #d4d4d4; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
        .view-toggle button.active {{ background: #0e639c; }}
        .unified {{ display: none; }}
        body.unified-view .split {{ display: none; }}
        body.unified-view .unified {{ display: flex; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>uni-diff</h1>
        <div class="stats">
            Similarity: {diff_result.similarity_ratio:.1%} |
            <span class="add">+{diff_result.stats.get('insertions', 0)}</span>
            <span class="del">-{diff_result.stats.get('deletions', 0)}</span>
            <span class="mod">~{diff_result.stats.get('modifications', 0)}</span>
        </div>
        <div class="view-toggle">
            <button class="active" onclick="setView('split')">Split</button>
            <button onclick="setView('unified')">Unified</button>
        </div>
    </div>
    <div class="container split">
        <div class="panel">
            <div class="panel-header old">- {html.escape(old_name)}</div>
            <div class="content" id="old-content">
{self._render_old_panel(diff_result)}
            </div>
        </div>
        <div class="panel">
            <div class="panel-header new">+ {html.escape(new_name)}</div>
            <div class="content" id="new-content">
{self._render_new_panel(diff_result)}
            </div>
        </div>
    </div>
    <div class="container unified">
        <div class="panel" style="max-width: 100%;">
            <div class="panel-header">Unified View</div>
            <div class="content" id="unified-content">
{self._render_unified(diff_result)}
            </div>
        </div>
    </div>
    <script>
        function setView(view) {{
            document.body.className = view === 'unified' ? 'unified-view' : '';
            document.querySelectorAll('.view-toggle button').forEach(btn => {{
                btn.classList.toggle('active', btn.textContent.toLowerCase() === view);
            }});
        }}
        // Sync scroll between panels
        const panels = document.querySelectorAll('.split .panel .content');
        panels.forEach(panel => {{
            panel.addEventListener('scroll', () => {{
                panels.forEach(p => {{ if (p !== panel) p.scrollTop = panel.scrollTop; }});
            }});
        }});
    </script>
</body>
</html>'''

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return None
        return html_content

    def _render_old_panel(self, diff_result: DiffResult) -> str:
        lines = []
        old_lines = diff_result.old_doc.full_text.splitlines() if diff_result.old_doc else []
        line_idx = 0

        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.old_end - hunk.old_start):
                    if line_idx < len(old_lines):
                        lines.append(self._line_html(line_idx + 1, old_lines[line_idx], 'equal'))
                        line_idx += 1

            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_end - hunk.old_start):
                    if line_idx < len(old_lines):
                        lines.append(self._line_html(line_idx + 1, old_lines[line_idx], 'delete'))
                        line_idx += 1

            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_end - hunk.new_start):
                    lines.append(self._line_html('', '', 'empty'))

            elif hunk.diff_type == DiffType.REPLACE:
                for i in range(hunk.old_end - hunk.old_start):
                    if line_idx < len(old_lines):
                        lines.append(self._line_html(line_idx + 1, old_lines[line_idx], 'modify'))
                        line_idx += 1
                extra_new = (hunk.new_end - hunk.new_start) - (hunk.old_end - hunk.old_start)
                for i in range(max(0, extra_new)):
                    lines.append(self._line_html('', '', 'empty'))

        return '\n'.join(lines)

    def _render_new_panel(self, diff_result: DiffResult) -> str:
        lines = []
        new_lines = diff_result.new_doc.full_text.splitlines() if diff_result.new_doc else []
        line_idx = 0

        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.new_end - hunk.new_start):
                    if line_idx < len(new_lines):
                        lines.append(self._line_html(line_idx + 1, new_lines[line_idx], 'equal'))
                        line_idx += 1

            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_end - hunk.old_start):
                    lines.append(self._line_html('', '', 'empty'))

            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_end - hunk.new_start):
                    if line_idx < len(new_lines):
                        lines.append(self._line_html(line_idx + 1, new_lines[line_idx], 'insert'))
                        line_idx += 1

            elif hunk.diff_type == DiffType.REPLACE:
                extra_old = (hunk.old_end - hunk.old_start) - (hunk.new_end - hunk.new_start)
                for i in range(max(0, extra_old)):
                    lines.append(self._line_html('', '', 'empty'))
                for i in range(hunk.new_end - hunk.new_start):
                    if line_idx < len(new_lines):
                        lines.append(self._line_html(line_idx + 1, new_lines[line_idx], 'insert'))
                        line_idx += 1

        return '\n'.join(lines)

    def _render_unified(self, diff_result: DiffResult) -> str:
        lines = []
        old_lines = diff_result.old_doc.full_text.splitlines() if diff_result.old_doc else []
        new_lines = diff_result.new_doc.full_text.splitlines() if diff_result.new_doc else []
        old_idx = 0
        new_idx = 0

        for hunk in diff_result.hunks:
            if hunk.diff_type == DiffType.EQUAL:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._line_html(f'{old_idx+1}', old_lines[old_idx], 'equal'))
                        old_idx += 1
                        new_idx += 1

            elif hunk.diff_type == DiffType.DELETE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._line_html(f'-{old_idx+1}', old_lines[old_idx], 'delete'))
                        old_idx += 1

            elif hunk.diff_type == DiffType.INSERT:
                for i in range(hunk.new_end - hunk.new_start):
                    if new_idx < len(new_lines):
                        lines.append(self._line_html(f'+{new_idx+1}', new_lines[new_idx], 'insert'))
                        new_idx += 1

            elif hunk.diff_type == DiffType.REPLACE:
                for i in range(hunk.old_end - hunk.old_start):
                    if old_idx < len(old_lines):
                        lines.append(self._line_html(f'-{old_idx+1}', old_lines[old_idx], 'delete'))
                        old_idx += 1
                for i in range(hunk.new_end - hunk.new_start):
                    if new_idx < len(new_lines):
                        lines.append(self._line_html(f'+{new_idx+1}', new_lines[new_idx], 'insert'))
                        new_idx += 1

        return '\n'.join(lines)

    def _line_html(self, num: Union[int, str], text: str, cls: str) -> str:
        escaped = html.escape(text) if text else '&nbsp;'
        return f'                <div class="line {cls}"><span class="line-num">{num}</span><span class="line-text">{escaped}</span></div>'
