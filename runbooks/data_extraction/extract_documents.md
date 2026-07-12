# Document Extraction Agent

Use this runbook to extract text from documents (PDFs, scans, images) using intelligent OCR.

## Input Variables
- `source_path`: Path to document or folder of documents
- `output_path`: Where to save extracted text (optional, defaults to workspace)
- `force_extractor`: Force a specific extractor (optional: tesseract|docling|easyocr|surya|auto)

## Process

1. **Analyze Document**
   - Type: Check if PDF, image, scanned document
   - Detect: Document quality and type

2. **Extract Text**
   - Use intelligent cascading: Tesseract → Docling → EasyOCR → Surya
   - Target confidence: >= 0.7
   
3. **Save Output**
   - JSON with text, metadata, confidence
   - Mark source and extraction info

## Example Usage

```
Task: Extract text from d:\data\documents\invoice.pdf saving to workspace\invoice.txt
```

## Expected Output

JSON file with:
- `text`: Extracted content
- `confidence`: Quality score (0-1)
- `extractor_used`: Which OCR succeeded
- `page_count`: Number of pages
- `extraction_time_ms`: Processing time