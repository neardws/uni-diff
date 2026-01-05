from abc import ABC, abstractmethod
from typing import Optional, Union
import sys

from diff.engine import DiffResult


class BaseRenderer(ABC):
    """Abstract base class for all renderers."""

    @property
    @abstractmethod
    def output_extension(self) -> str:
        """File extension for the output format."""
        pass

    @abstractmethod
    def render(self, diff_result: DiffResult, output: Optional[str] = None) -> Union[str, bytes, None]:
        """
        Render the diff result.
        
        Args:
            diff_result: The diff result to render
            output: Optional output file path. If None, returns the result or prints to stdout.
            
        Returns:
            The rendered content as string/bytes, or None if written to file/stdout.
        """
        pass

    def write_output(self, content: Union[str, bytes], output: Optional[str] = None) -> None:
        """Write content to file or stdout."""
        if output:
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(output, mode) as f:
                f.write(content)
        else:
            if isinstance(content, bytes):
                sys.stdout.buffer.write(content)
            else:
                print(content)
