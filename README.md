# uni-diff

[![GitHub release](https://img.shields.io/github/v/release/neardws/uni-diff)](https://github.com/neardws/uni-diff/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Universal file diff tool - compare any files with multiple output formats.

![PNG Output Example](https://raw.githubusercontent.com/neardws/uni-diff/main/docs/images/diff_example.png)

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

### Homebrew (macOS/Linux)

```bash
brew tap neardws/tap
brew install uni-diff
```

Or in one command:
```bash
brew install neardws/tap/uni-diff
```

### pip

```bash
# Basic installation (text diff only)
pip install uni-diff

# With all format support
pip install "uni-diff[all]"

# Or install specific format support
pip install "uni-diff[pdf,docx,xlsx,pptx,image,png]"
```

### From source

```bash
git clone https://github.com/neardws/uni-diff.git
cd uni-diff
pip install -e ".[all]"
```

### System Dependencies (Optional)

For PDF support:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

For OCR support:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## Quick Start

```bash
# Compare two text files
uni-diff old.txt new.txt

# Compare with PNG image output
uni-diff old.py new.py -f png -o diff.png

# Compare Word documents with HTML output
uni-diff old.docx new.docx -f html -o diff.html

# Get JSON output for programmatic use
uni-diff config.yaml new_config.yaml -f json

# Show summary only
uni-diff old.pdf new.pdf --summary
```

## Usage

```
uni-diff [OPTIONS] OLD_FILE NEW_FILE

Arguments:
  OLD_FILE    Path to the old/original file
  NEW_FILE    Path to the new/modified file

Options:
  -f, --format FORMAT    Output format: ansi, tui, html, png, json (default: ansi)
  -o, --output FILE      Output file path (default: stdout for text formats)
  -c, --context N        Number of context lines (default: 3)
  --no-color             Disable colored output
  --block-diff           Use block-level diff for better positioning
  -q, --quiet            Only output if there are differences
  -s, --summary          Only show summary statistics
  -v, --version          Show version
  -h, --help             Show help
```

## Output Formats

### ANSI (default)

Colored diff output in terminal, similar to `git diff`:

```
━━━ uni-diff ━━━
--- old.txt
+++ new.txt

   1 - Hello World
   1 + Hello Universe
   2   This is line two.
   3 - Line three here.
   3 + Line three has been modified.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Similarity: 54.5% | +1 -0 ~2
```

### PNG

Visual comparison image with side-by-side panels:
- Red highlight: deleted/modified content (old file)
- Green highlight: added/modified content (new file)
- Statistics footer showing similarity ratio

### HTML

Interactive web page with:
- Split and unified views
- Synchronized scrolling
- Dark theme support

### JSON

Structured data for programmatic use:

```json
{
  "summary": {
    "similarity_ratio": 0.545,
    "has_changes": true,
    "stats": {
      "insertions": 1,
      "deletions": 0,
      "modifications": 2
    }
  },
  "hunks": [...]
}
```

### TUI

Interactive terminal interface with:
- Split/unified view toggle (press `v`)
- Scroll navigation (`j`/`k`, `d`/`u`, `g`/`G`)
- Syntax highlighting for changes

## Supported File Types

| Format | Extensions | Description |
|--------|------------|-------------|
| Text | .txt, .md, .rst | Plain text files |
| Code | .py, .js, .ts, .java, .c, .cpp, .go, .rs, .rb | Source code |
| Config | .json, .yaml, .yml, .toml, .ini, .xml | Configuration files |
| Web | .html, .css | Web files |
| Data | .csv, .tsv | Data files |
| PDF | .pdf | PDF documents |
| Word | .docx | Microsoft Word |
| Excel | .xlsx, .xls | Microsoft Excel |
| PowerPoint | .pptx | Microsoft PowerPoint |
| Images | .png, .jpg, .gif, .bmp, .tiff | Images (with OCR) |

## Python API

```python
from converters import get_converter
from diff import DiffEngine
from renderers import get_renderer

# Convert files to unified format
old_doc = get_converter('old.pdf').convert('old.pdf')
new_doc = get_converter('new.pdf').convert('new.pdf')

# Compute differences
engine = DiffEngine(context_lines=3)
result = engine.diff(old_doc, new_doc)

# Check results
print(f"Similarity: {result.similarity_ratio:.1%}")
print(f"Has changes: {result.has_changes}")

# Render to different formats
json_renderer = get_renderer('json')
json_output = json_renderer.render(result)

html_renderer = get_renderer('html')
html_renderer.render(result, 'diff.html')

png_renderer = get_renderer('png')
png_renderer.render(result, 'diff.png')
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Files are identical |
| 1 | Files are different |
| 2 | Error occurred |

## Testing

```bash
# Run all tests
python -m unittest discover tests/ -v

# Run specific test file
python -m unittest tests/test_diff_engine.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/neardws/uni-diff)
- [Releases](https://github.com/neardws/uni-diff/releases)
- [Homebrew Tap](https://github.com/neardws/homebrew-tap)
