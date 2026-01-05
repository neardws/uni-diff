from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import difflib

from converters.base import ConvertedDocument, TextBlock


class DiffType(Enum):
    EQUAL = 'equal'
    INSERT = 'insert'
    DELETE = 'delete'
    REPLACE = 'replace'


@dataclass
class DiffHunk:
    """Represents a single difference between two documents."""
    diff_type: DiffType
    old_text: str = ""
    new_text: str = ""
    old_start: int = 0
    old_end: int = 0
    new_start: int = 0
    new_end: int = 0
    old_blocks: List[TextBlock] = field(default_factory=list)
    new_blocks: List[TextBlock] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.diff_type.value,
            'old_text': self.old_text,
            'new_text': self.new_text,
            'old_range': [self.old_start, self.old_end],
            'new_range': [self.new_start, self.new_end],
            'old_blocks': [b.to_dict() for b in self.old_blocks],
            'new_blocks': [b.to_dict() for b in self.new_blocks],
            'metadata': self.metadata
        }


@dataclass
class DiffResult:
    """Result of comparing two documents."""
    hunks: List[DiffHunk] = field(default_factory=list)
    old_doc: Optional[ConvertedDocument] = None
    new_doc: Optional[ConvertedDocument] = None
    similarity_ratio: float = 0.0
    stats: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'similarity_ratio': self.similarity_ratio,
            'stats': self.stats,
            'hunks': [h.to_dict() for h in self.hunks],
            'old_source': self.old_doc.source_path if self.old_doc else None,
            'new_source': self.new_doc.source_path if self.new_doc else None
        }

    @property
    def has_changes(self) -> bool:
        return any(h.diff_type != DiffType.EQUAL for h in self.hunks)

    @property
    def changes_only(self) -> List[DiffHunk]:
        return [h for h in self.hunks if h.diff_type != DiffType.EQUAL]


class DiffEngine:
    """Engine for computing differences between documents."""

    def __init__(self, context_lines: int = 3):
        self.context_lines = context_lines

    def diff(self, old_doc: ConvertedDocument, new_doc: ConvertedDocument) -> DiffResult:
        """Compare two documents and return the differences."""
        old_lines = old_doc.full_text.splitlines(keepends=True)
        new_lines = new_doc.full_text.splitlines(keepends=True)

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        similarity = matcher.ratio()

        hunks = []
        stats = {'insertions': 0, 'deletions': 0, 'modifications': 0, 'unchanged': 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            old_text = ''.join(old_lines[i1:i2])
            new_text = ''.join(new_lines[j1:j2])

            old_blocks = self._find_blocks_in_range(old_doc.blocks, i1, i2)
            new_blocks = self._find_blocks_in_range(new_doc.blocks, j1, j2)

            if tag == 'equal':
                diff_type = DiffType.EQUAL
                stats['unchanged'] += i2 - i1
            elif tag == 'insert':
                diff_type = DiffType.INSERT
                stats['insertions'] += j2 - j1
            elif tag == 'delete':
                diff_type = DiffType.DELETE
                stats['deletions'] += i2 - i1
            elif tag == 'replace':
                diff_type = DiffType.REPLACE
                stats['modifications'] += max(i2 - i1, j2 - j1)

            hunks.append(DiffHunk(
                diff_type=diff_type,
                old_text=old_text,
                new_text=new_text,
                old_start=i1,
                old_end=i2,
                new_start=j1,
                new_end=j2,
                old_blocks=old_blocks,
                new_blocks=new_blocks
            ))

        return DiffResult(
            hunks=hunks,
            old_doc=old_doc,
            new_doc=new_doc,
            similarity_ratio=similarity,
            stats=stats
        )

    def diff_blocks(self, old_doc: ConvertedDocument, new_doc: ConvertedDocument) -> DiffResult:
        """Compare documents at the block level for more precise positioning."""
        old_texts = [b.text for b in old_doc.blocks]
        new_texts = [b.text for b in new_doc.blocks]

        matcher = difflib.SequenceMatcher(None, old_texts, new_texts)
        similarity = matcher.ratio()

        hunks = []
        stats = {'insertions': 0, 'deletions': 0, 'modifications': 0, 'unchanged': 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            old_blocks = old_doc.blocks[i1:i2]
            new_blocks = new_doc.blocks[j1:j2]
            old_text = '\n'.join(b.text for b in old_blocks)
            new_text = '\n'.join(b.text for b in new_blocks)

            if tag == 'equal':
                diff_type = DiffType.EQUAL
                stats['unchanged'] += i2 - i1
            elif tag == 'insert':
                diff_type = DiffType.INSERT
                stats['insertions'] += j2 - j1
            elif tag == 'delete':
                diff_type = DiffType.DELETE
                stats['deletions'] += i2 - i1
            elif tag == 'replace':
                diff_type = DiffType.REPLACE
                stats['modifications'] += max(i2 - i1, j2 - j1)

            hunks.append(DiffHunk(
                diff_type=diff_type,
                old_text=old_text,
                new_text=new_text,
                old_start=i1,
                old_end=i2,
                new_start=j1,
                new_end=j2,
                old_blocks=old_blocks,
                new_blocks=new_blocks
            ))

        return DiffResult(
            hunks=hunks,
            old_doc=old_doc,
            new_doc=new_doc,
            similarity_ratio=similarity,
            stats=stats
        )

    def _find_blocks_in_range(self, blocks: List[TextBlock], start_line: int, end_line: int) -> List[TextBlock]:
        """Find blocks that fall within the given line range."""
        result = []
        for block in blocks:
            line_num = block.metadata.get('line_number', 0)
            if line_num == 0:
                estimated_line = int(block.y / 12)
                if start_line <= estimated_line < end_line:
                    result.append(block)
            else:
                if start_line < line_num <= end_line:
                    result.append(block)
        return result

    def unified_diff(self, old_doc: ConvertedDocument, new_doc: ConvertedDocument,
                     old_label: str = "old", new_label: str = "new") -> str:
        """Generate unified diff format output."""
        old_lines = old_doc.full_text.splitlines(keepends=True)
        new_lines = new_doc.full_text.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=old_label,
            tofile=new_label,
            n=self.context_lines
        )
        return ''.join(diff)

    def context_diff(self, old_doc: ConvertedDocument, new_doc: ConvertedDocument,
                     old_label: str = "old", new_label: str = "new") -> str:
        """Generate context diff format output."""
        old_lines = old_doc.full_text.splitlines(keepends=True)
        new_lines = new_doc.full_text.splitlines(keepends=True)

        diff = difflib.context_diff(
            old_lines, new_lines,
            fromfile=old_label,
            tofile=new_label,
            n=self.context_lines
        )
        return ''.join(diff)
