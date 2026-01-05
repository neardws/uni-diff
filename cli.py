#!/usr/bin/env python3
"""
uni-diff: Universal file diff tool

Compare any files - PDF, DOCX, XLSX, PPTX, images, and text files.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters import get_converter
from diff import DiffEngine
from renderers import get_renderer, RENDERERS


def main():
    parser = argparse.ArgumentParser(
        prog='uni-diff',
        description='Universal file diff tool - compare any files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  uni-diff old.pdf new.pdf                    # Compare PDFs, output to terminal
  uni-diff old.docx new.docx -f html -o diff.html  # Compare Word docs, HTML output
  uni-diff a.txt b.txt -f png -o diff.png     # Compare text files, PNG output
  uni-diff doc.xlsx doc2.xlsx -f tui          # Compare Excel files in TUI
  uni-diff old.md new.md -f json              # Compare Markdown, JSON output

Supported input formats:
  PDF (.pdf), Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
  Images (.png, .jpg, .gif, .bmp, .tiff) - with OCR support
  Text files (.txt, .md, .json, .xml, .py, .js, etc.)

Supported output formats:
  ansi (default) - Colored terminal output
  tui            - Interactive terminal UI
  html           - Interactive HTML page
  png            - Visual comparison image
  json           - Structured JSON data
'''
    )

    parser.add_argument('old_file', help='Path to the old/original file')
    parser.add_argument('new_file', help='Path to the new/modified file')
    parser.add_argument(
        '-f', '--format',
        choices=list(RENDERERS.keys()),
        default='ansi',
        help='Output format (default: ansi)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout for text formats)'
    )
    parser.add_argument(
        '-c', '--context',
        type=int,
        default=3,
        help='Number of context lines (default: 3)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    parser.add_argument(
        '--block-diff',
        action='store_true',
        help='Use block-level diff for better positioning (PDF, DOCX)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Only output if there are differences'
    )
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Only show summary statistics'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='uni-diff 0.1.0'
    )

    args = parser.parse_args()

    if not os.path.exists(args.old_file):
        print(f"Error: File not found: {args.old_file}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.new_file):
        print(f"Error: File not found: {args.new_file}", file=sys.stderr)
        sys.exit(1)

    try:
        old_converter = get_converter(args.old_file)
        new_converter = get_converter(args.new_file)

        if not args.quiet:
            print(f"Converting {os.path.basename(args.old_file)}...", file=sys.stderr)
        old_doc = old_converter.convert(args.old_file)

        if not args.quiet:
            print(f"Converting {os.path.basename(args.new_file)}...", file=sys.stderr)
        new_doc = new_converter.convert(args.new_file)

        engine = DiffEngine(context_lines=args.context)

        if args.block_diff:
            diff_result = engine.diff_blocks(old_doc, new_doc)
        else:
            diff_result = engine.diff(old_doc, new_doc)

        if args.quiet and not diff_result.has_changes:
            sys.exit(0)

        if args.summary:
            stats = diff_result.stats
            print(f"Similarity: {diff_result.similarity_ratio:.1%}")
            print(f"Insertions: {stats.get('insertions', 0)}")
            print(f"Deletions:  {stats.get('deletions', 0)}")
            print(f"Modifications: {stats.get('modifications', 0)}")
            sys.exit(0 if not diff_result.has_changes else 1)

        renderer = get_renderer(args.format)

        if hasattr(renderer, 'color') and args.no_color:
            renderer.color = False

        result = renderer.render(diff_result, args.output)

        if result is not None and args.output is None:
            if isinstance(result, bytes):
                sys.stdout.buffer.write(result)
            else:
                print(result)

        if args.output and not args.quiet:
            print(f"Output written to: {args.output}", file=sys.stderr)

        sys.exit(0 if not diff_result.has_changes else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if os.environ.get('DEBUG'):
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
