# Docling Testbed

## Overview
A comprehensive testbed for exploring [Docling](https://github.com/DS4SD/docling), a powerful PDF document conversion library. This project demonstrates various use cases including basic PDF conversion, RAG (Retrieval Augmented Generation) preparation, table extraction, ChromaDB vector database integration, and advanced configuration options.

## Features

- **PDF to JSON Conversion**: Convert PDF documents to structured JSON format
- **RAG-Ready Chunking**: Prepare PDF content for vector embeddings with intelligent chunking and metadata
- **ChromaDB Integration**: Ingest and query RAG chunks using ChromaDB vector database with MPNet embeddings
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

### ChromaDB Vector Database Integration

#### Ingesting RAG Chunks into ChromaDB
After preparing your RAG chunks, ingest them into ChromaDB for semantic search:

**Basic ingestion:**
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json
```

**Custom collection name:**
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --collection my_financial_docs
```

**Filter content types (ingest only tables):**
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --include-types table
```

**Exclude certain types:**
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --exclude-types picture,caption
```

**Reset collection (clear existing data):**
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --reset
```

**Ingestion Options:**
- `--collection NAME`: Custom collection name (default: `docling_rag_chunks`)
- `--reset`: Delete existing collection before ingestion
- `--include-types`: Comma-separated list of content types to include
- `--exclude-types`: Comma-separated list of content types to exclude
- `--batch-size`: Batch size for ingestion (default: 100)

**Configuration:**
- Vector database stored in `./vectordb` directory
- Uses `all-mpnet-base-v2` embedding model (high-quality semantic search)
- Preserves all metadata for filtering and attribution

#### Querying ChromaDB

**Basic similarity search:**
```bash
python src/query_chromadb.py "net interest income"
```

**Search with more results:**
```bash
python src/query_chromadb.py "revenue growth" --n-results 10
```

**Filter by content type:**
```bash
python src/query_chromadb.py "financial data" --content-type table
```

**Search only tables:**
```bash
python src/query_chromadb.py "consolidated statements" --tables-only
```

**Filter by page range:**
```bash
python src/query_chromadb.py "risk factors" --page-min 10 --page-max 20
```

**Show full content (not truncated):**
```bash
python src/query_chromadb.py "credit losses" --full
```

**Collection statistics:**
```bash
python src/query_chromadb.py --stats
```

**Query Options:**
- `--collection NAME`: Query specific collection
- `--n-results N`: Number of results to return (default: 5)
- `--content-type TYPE`: Filter by content type (e.g., table, text, section_header)
- `--tables-only`: Search only table content
- `--page-min N`: Minimum page number
- `--page-max N`: Maximum page number
- `--full`: Show full content instead of preview
- `--stats`: Show collection statistics

#### RAG Query Examples
See comprehensive examples of different query patterns:
```bash
python src/example_query_rag.py
```

**Examples include:**
- Basic similarity search
- Table-only search for structured data
- Filtered search by content type
- Page range search
- Multi-query RAG pattern
- Hybrid search (combining text and tables)
- Collection statistics

## Project Structure

```
docling_testbed/
├── src/
│   ├── example_basic.py          # Basic PDF conversion demo
│   ├── example_rag_simple.py     # Simple RAG preparation
│   ├── example_with_options.py   # Advanced configuration demo
│   ├── example_query_rag.py      # ChromaDB query examples
│   ├── pdf_to_json.py           # PDF to JSON converter
│   ├── pdf_to_rag.py            # RAG-optimized chunking with tables
│   ├── ingest_to_chromadb.py    # Ingest RAG chunks to ChromaDB
│   ├── query_chromadb.py        # Query ChromaDB vector database
│   └── chromadb_config.py       # ChromaDB configuration settings
├── data/
│   ├── test_doc.pdf             # Sample PDF for testing
│   ├── 10q_3q25_rag.json        # Sample RAG chunks from 10-Q filing
│   └── *.json                   # Generated output files
├── vectordb/                     # ChromaDB persistence directory
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

### Vector Database Integration
- ChromaDB persistent storage
- MPNet embeddings for high-quality semantic search
- Metadata filtering for precise retrieval
- Batch ingestion with progress tracking
- Support for both text and table chunks

## ChromaDB Query Patterns

The included examples demonstrate several powerful query patterns for RAG applications:

1. **Basic Similarity Search**: Find semantically similar content
2. **Table-Only Search**: Extract structured financial data
3. **Filtered Search**: Query specific content types or page ranges
4. **Multi-Query RAG**: Decompose complex questions into sub-queries
5. **Hybrid Search**: Combine narrative text with tabular data

These patterns enable sophisticated document retrieval for question-answering, summarization, and analysis tasks.

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License.