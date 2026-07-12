"""
CLI tool for document extraction integration with ZIVA Agent.

Usage:
    python scripts/extract_docs.py <file_path> [--output <path>] [--extractor <name>]
"""
from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_studio.mcp_document import extract_document, DocumentExtractor


def main():
    parser = argparse.ArgumentParser(description="Extract text from documents using ZIVA")
    parser.add_argument("file_path", help="Path to PDF or image file")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument("--extractor", "-e",
                        choices=["tesseract", "docling", "easyocr", "surya", "auto"],
                        default="auto",
                        help="Force specific extractor (default: auto)")
    parser.add_argument("--min-confidence", "-c", type=float, default=0.7,
                        help="Minimum confidence threshold (0-1)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--check-extractors", action="store_true",
                        help="Show available extractors and exit")

    args = parser.parse_args()

    # Check extractors
    if args.check_extractors:
        extractor = DocumentExtractor()
        available = extractor.get_available_extractors()
        print("Available extractors:")
        for name in available:
            print(f"  ✓ {name}")
        if not available:
            print("  No extractors available. Install dependencies:")
            print("  pip install pytesseract pdf2image Pillow easyocr surya-ocr docling")
        return

    # Validate file
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Extract
    if args.verbose:
        print(f"Extracting from: {file_path}")
        print(f"Extractor: {args.extractor}")

    result = extract_document(
        str(file_path),
        force_extractor=args.extractor if args.extractor != "auto" else None,
        min_confidence=args.min_confidence
    )

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        if args.verbose:
            print(f"Saved to: {output_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Summary
    if args.verbose:
        print(f"\nSummary:")
        print(f"  Extractor: {result['extractor_used']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Pages: {result['page_count']}")
        print(f"  Text length: {len(result['text'])} chars")
        if result.get('cache_hit'):
            print(f"  Cache: HIT")
        if result.get('error'):
            print(f"  Error: {result['error']}")


if __name__ == "__main__":
    main()