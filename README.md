# Docling Testbed

## Overview
A comprehensive testbed for exploring [Docling](https://github.com/DS4SD/docling), a powerful PDF document conversion library. This project demonstrates various use cases including basic PDF conversion, RAG (Retrieval Augmented Generation) preparation, table extraction, and advanced configuration options.

## Features

- **PDF to JSON Conversion**: Convert PDF documents to structured JSON format
- **RAG-Ready Chunking**: Prepare PDF content for vector embeddings with intelligent chunking and metadata
- **Table Extraction**: Extract and preserve table structures from PDFs with configurable accuracy modes
- **Advanced Options**: OCR support, customizable pipeline configurations, and format options
- **Multiple Examples**: From basic usage to advanced configurations

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Examples

#### 1. Simple PDF to JSON Conversion
Convert a PDF to Docling's JSON format:
```bash
python src/pdf_to_json.py data/test_doc.pdf data/test_doc.json
```

#### 2. Basic Document Inspection
Explore PDF structure and content:
```bash
python src/example_basic.py data/test_doc.pdf
```

#### 3. Simple RAG Preparation
Quick extraction for RAG applications:
```bash
python src/example_rag_simple.py data/test_doc.pdf data/output.json
```

### Advanced Usage

#### RAG-Optimized Chunking with Table Support
The `pdf_to_rag.py` script provides sophisticated chunking for RAG applications:

**Basic chunking (no tables):**
```bash
python src/pdf_to_rag.py data/test_doc.pdf data/output_rag.json
```

**With table extraction:**
```bash
python src/pdf_to_rag.py data/test_doc.pdf data/output_rag.json --include-tables
```

**Custom chunk sizes:**
```bash
python src/pdf_to_rag.py data/test_doc.pdf data/output_rag.json \
  --chunk-size 1500 \
  --overlap 300 \
  --include-tables
```

**Options:**
- `--chunk-size SIZE`: Maximum chunk size in characters (default: 1000)
- `--overlap SIZE`: Overlap between chunks in characters (default: 200)
- `--include-tables`: Enable table structure recognition and extraction

#### Advanced Configuration Options
Customize OCR, table extraction, and other pipeline options:
```bash
python src/example_with_options.py data/test_doc.pdf data/output.json
```

## Project Structure

```
docling_testbed/
├── src/
│   ├── example_basic.py          # Basic PDF conversion demo
│   ├── example_rag_simple.py     # Simple RAG preparation
│   ├── example_with_options.py   # Advanced configuration demo
│   ├── pdf_to_json.py           # PDF to JSON converter
│   └── pdf_to_rag.py            # RAG-optimized chunking with tables
├── data/
│   ├── test_doc.pdf             # Sample PDF for testing
│   └── *.json                   # Generated output files
├── tests/                        # Test suite
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Output Formats

### RAG Output Structure
The `pdf_to_rag.py` script generates JSON with:
```json
{
  "total_chunks": 2166,
  "chunks": [
    {
      "chunk_id": 1,
      "text": "Chunk content...",
      "metadata": {
        "source": "document.pdf",
        "content_type": "section_header",
        "page": 1,
        "chunk_index": 0,
        "total_chunks": 1,
        "is_partial": false
      }
    }
  ]
}
```

**Content Types:**
- `text`: Regular paragraphs
- `section_header`: Headings and titles
- `list_item`: Bullet points and lists
- `table`: Extracted tables (with `--include-tables`)
- `code`: Code blocks
- `caption`: Image/figure captions
- `picture`: Image descriptions

## Key Features

### Intelligent Chunking
- Preserves sentence boundaries
- Configurable overlap for context retention
- Metadata for filtering and retrieval

### Table Extraction
- Accurate table structure recognition
- Markdown format conversion
- Preserves cell relationships

### Metadata Enrichment
- Page numbers for source tracking
- Content type classification
- Chunk relationships for partial content

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License.