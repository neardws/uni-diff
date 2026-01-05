# uni-diff

Universal file diff tool - compare any files with multiple output formats.

## Features

- **Multiple input formats**: PDF, DOCX, XLSX, PPTX, images (with OCR), and all text files
- **Multiple output formats**: 
  - ANSI (colored terminal)
  - TUI (interactive terminal UI)
  - HTML (interactive web page)
  - PNG (visual comparison image)
  - JSON (structured data)
- **Smart conversion**: Automatically detects file type and uses appropriate converter
- **Block-level diff**: Optional positioning information for visual output

## Installation

```bash
# Basic installation (text diff only)
pip install -e .

# With all format support
pip install -e ".[all]"

# Or install specific format support
pip install -e ".[pdf,docx,xlsx,pptx,image,png]"
```

### System Dependencies

For PDF support (optional):
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

For OCR support (optional):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## Usage

```bash
# Basic usage - compare two files with colored terminal output
uni-diff old.txt new.txt

# Compare PDFs with HTML output
uni-diff old.pdf new.pdf -f html -o comparison.html

# Compare Word documents with PNG output
uni-diff old.docx new.docx -f png -o diff.png

# Interactive TUI mode
uni-diff old.xlsx new.xlsx -f tui

# JSON output for programmatic use
uni-diff old.md new.md -f json > diff.json

# Summary only
uni-diff old.py new.py --summary

# Quiet mode (exit code only)
uni-diff old.txt new.txt -q
```

## Output Formats

### ANSI (default)
Colored diff output in terminal, similar to `git diff`.

### TUI
Interactive terminal interface with:
- Split/unified view toggle (press `v`)
- Scroll navigation (`j`/`k`, `d`/`u`, `g`/`G`)
- Syntax highlighting for changes

### HTML
Interactive web page with:
- Split and unified views
- Synchronized scrolling
- Dark theme

### PNG
Visual comparison image with:
- Side-by-side panels
- Color-coded changes (red=deleted, green=inserted, yellow=modified)
- Statistics footer

### JSON
Structured data including:
- Similarity ratio
- Change statistics
- Detailed hunks with text and positions

## Supported File Types

| Format | Extension | Converter |
|--------|-----------|-----------|
| PDF | .pdf | pdftotext or pymupdf |
| Word | .docx | python-docx or pandoc |
| Excel | .xlsx, .xls | openpyxl |
| PowerPoint | .pptx | python-pptx |
| Images | .png, .jpg, .gif, etc. | Pillow + OCR |
| Text | .txt, .md, .json, .py, etc. | Built-in |

## Python API

```python
from converters import get_converter
from diff import DiffEngine
from renderers import get_renderer

# Convert files
old_doc = get_converter('old.pdf').convert('old.pdf')
new_doc = get_converter('new.pdf').convert('new.pdf')

# Compute diff
engine = DiffEngine()
result = engine.diff(old_doc, new_doc)

# Render output
renderer = get_renderer('html')
html = renderer.render(result)
```

## License

MIT
