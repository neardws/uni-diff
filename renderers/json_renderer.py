from typing import Optional, Union
import json

from .base import BaseRenderer
from diff.engine import DiffResult


class JSONRenderer(BaseRenderer):
    """Render diff results as structured JSON."""

    def __init__(self, indent: int = 2, include_full_text: bool = False):
        self.indent = indent
        self.include_full_text = include_full_text

    @property
    def output_extension(self) -> str:
        return '.json'

    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> Union[str, None]:
        data = {
            'summary': {
                'similarity_ratio': diff_result.similarity_ratio,
                'has_changes': diff_result.has_changes,
                'stats': diff_result.stats,
            },
            'files': {
                'old': {
                    'path': diff_result.old_doc.source_path if diff_result.old_doc else None,
                    'type': diff_result.old_doc.source_type if diff_result.old_doc else None,
                    'page_count': diff_result.old_doc.page_count if diff_result.old_doc else 0,
                },
                'new': {
                    'path': diff_result.new_doc.source_path if diff_result.new_doc else None,
                    'type': diff_result.new_doc.source_type if diff_result.new_doc else None,
                    'page_count': diff_result.new_doc.page_count if diff_result.new_doc else 0,
                }
            },
            'hunks': [h.to_dict() for h in diff_result.hunks],
            'changes_only': [h.to_dict() for h in diff_result.changes_only],
        }

        if self.include_full_text:
            data['files']['old']['full_text'] = diff_result.old_doc.full_text if diff_result.old_doc else ""
            data['files']['new']['full_text'] = diff_result.new_doc.full_text if diff_result.new_doc else ""

        json_str = json.dumps(data, indent=self.indent, ensure_ascii=False)

        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_str)
            return None
        return json_str
