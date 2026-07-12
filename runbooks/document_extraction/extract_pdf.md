# Document Extraction Task

Extract text from the document using intelligent OCR.

## Source Document

```
C:\Users\M Mohsin Aleem\Desktop\S.R.O 2477(1) 2025 22-12-2025 NOTIFICATION.PDF
```

## Process

1. Use the document extractor to extract text from the PDF
2. Auto-detect document type (native PDF)
3. Target confidence: >= 0.7
4. Save extracted text to workspace

## Output Format

Save result as JSON with:
- text: extracted content
- confidence: quality score (0-1)
- extractor_used: which OCR was used (docling, tesseract, etc.)
- page_count: number of pages
- extraction_time_ms: processing time

## Expected Extractors

The extractor will try in order:
1. Docling - best for native/searchable PDFs
2. Tesseract - fallback OCR
3. EasyOCR - Python OCR
4. Surya - Microsoft OCR (last resort)

The document is a scanned PDF containing S.R.O (Statutory Regulatory Order) notification.