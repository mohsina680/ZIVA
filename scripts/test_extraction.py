"""
Quick test script to verify document extraction works.
Run: python scripts/test_extraction.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_studio.mcp_document import DocumentExtractor

def main():
    print("[*] ZIVA Document Extractor - Quick Test\n")

    # Create extractor
    extractor = DocumentExtractor()

    # Check available extractors
    available = extractor.get_available_extractors()
    print("[+] Available Extractors:")
    for name in available:
        print(f"   ✓ {name}")

    if not available:
        print("\n[!] No extractractors available!")
        print("\nInstall dependencies:")
        print("  pip install pytesseract pdf2image Pillow easyocr surya-ocr docling")
        print("\nFor Tesseract, also install:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux:  sudo apt-get install tesseract-ocr poppler-utils")
        return

    # Show cache stats
    print(f"\n[*] Cache Status:")
    stats = extractor.get_cache_stats()
    print(f"   Entries: {stats['entries']}")
    print(f"   Location: {stats['cache_dir']}")

    print("\n[OK] Document Extractor is ready to use!")
    print("\n[*] Usage Examples:")
    print("""
1. CLI:
   python scripts/extract_docs.py document.pdf --output result.json -v
   python scripts/extract_docs.py scan.jpg --extractor tesseract

2. Python:
   from agentic_studio.mcp_document import extract_document
   result = extract_document("document.pdf")
   print(result['text'])

3. MCP Server (for Claude Code):
   python -m src.agentic_studio.mcp_document.mcp_server

4. Batch Processing:
   python -c "from agentic_studio.mcp_document import batch_extract; \\
       results = batch_extract(['doc1.pdf', 'doc2.jpg'], parallel=True)"
    """)


if __name__ == "__main__":
    main()