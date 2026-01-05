from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class TextBlock:
    """Represents a block of text with position information."""
    text: str
    page: int = 0
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'page': self.page,
            'bbox': [self.x, self.y, self.width, self.height],
            'metadata': self.metadata
        }


@dataclass
class ConvertedDocument:
    """Unified intermediate format for all document types."""
    blocks: List[TextBlock] = field(default_factory=list)
    full_text: str = ""
    page_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    source_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_path': self.source_path,
            'source_type': self.source_type,
            'page_count': self.page_count,
            'full_text': self.full_text,
            'blocks': [b.to_dict() for b in self.blocks],
            'metadata': self.metadata
        }

    @classmethod
    def from_text(cls, text: str, source_path: str = "", source_type: str = "text"):
        """Create a ConvertedDocument from plain text."""
        lines = text.split('\n')
        blocks = []
        for i, line in enumerate(lines):
            if line.strip():
                blocks.append(TextBlock(
                    text=line,
                    page=0,
                    y=i * 12.0,
                    height=12.0
                ))
        return cls(
            blocks=blocks,
            full_text=text,
            page_count=1,
            source_path=source_path,
            source_type=source_type
        )


class BaseConverter(ABC):
    """Abstract base class for all document converters."""

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """List of file extensions this converter supports."""
        pass

    @abstractmethod
    def convert(self, file_path: str) -> ConvertedDocument:
        """Convert a file to the unified intermediate format."""
        pass

    def can_convert(self, file_path: str) -> bool:
        """Check if this converter can handle the given file."""
        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
