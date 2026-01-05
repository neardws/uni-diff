from .base import BaseRenderer
from .png import PNGRenderer
from .html import HTMLRenderer
from .json_renderer import JSONRenderer
from .tui import TUIRenderer
from .ansi import ANSIRenderer

RENDERERS = {
    'png': PNGRenderer,
    'html': HTMLRenderer,
    'json': JSONRenderer,
    'tui': TUIRenderer,
    'ansi': ANSIRenderer,
    'terminal': ANSIRenderer,
}

def get_renderer(format: str) -> BaseRenderer:
    """Get appropriate renderer based on format name."""
    renderer_class = RENDERERS.get(format.lower())
    if renderer_class is None:
        raise ValueError(f"Unknown format: {format}. Available: {list(RENDERERS.keys())}")
    return renderer_class()

__all__ = [
    'BaseRenderer', 'PNGRenderer', 'HTMLRenderer',
    'JSONRenderer', 'TUIRenderer', 'ANSIRenderer',
    'RENDERERS', 'get_renderer'
]
