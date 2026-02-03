# ChromaDB Quick Start Guide

This guide will help you quickly ingest your RAG data into ChromaDB and start querying it.

## Prerequisites

Ensure you have installed the dependencies:
```bash
pip install -r requirements.txt
```

## Step 1: Prepare RAG Data (if not already done)

If you don't have a RAG JSON file yet, create one from a PDF:

```bash
python src/pdf_to_rag.py your_document.pdf data/your_rag_data.json --include-tables
```

## Step 2: Ingest into ChromaDB

Ingest your RAG chunks into the vector database:

```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json
```

This will:
- Create a persistent ChromaDB database in `./vectordb`
- Use the `all-mpnet-base-v2` embedding model
- Process all 1,546 chunks with metadata
- Create a collection named `docling_rag_chunks`

Expected output:
```
Loading RAG data from data/10q_3q25_rag.json...
✓ Loaded 1546 chunks

Initializing ChromaDB client...
  Persistence directory: /path/to/vectordb
  Collection name: docling_rag_chunks
  Embedding model: sentence-transformers/all-mpnet-base-v2

✓ Collection ready: docling_rag_chunks
  Existing documents: 0

Preparing chunks for ingestion...
✓ Prepared 1546 chunks

Content type distribution:
  - caption: 90
  - checkbox_selected: 2
  - checkbox_unselected: 7
  - document_index: 11
  - footnote: 1
  - list_item: 138
  - picture: 32
  - section_header: 245
  - table: 629
  - text: 391

Ingesting chunks (batch size: 100)...
Ingesting: 100%|████████████████| 1546/1546 [02:15<00:00, 11.42chunk/s]

✓ Ingestion complete!
  Total documents in collection: 1546
```

## Step 3: Query the Database

### Basic Query

```bash
python src/query_chromadb.py "net interest income"
```

### Query Only Tables

```bash
python src/query_chromadb.py "consolidated statements of income" --tables-only
```

### Filter by Content Type

```bash
python src/query_chromadb.py "risk management" --content-type section_header
```

### Query Specific Page Range

```bash
python src/query_chromadb.py "credit losses" --page-min 20 --page-max 30
```

### Get More Results

```bash
python src/query_chromadb.py "revenue" --n-results 10
```

## Step 4: Explore Example Patterns

Run the comprehensive examples script:

```bash
python src/example_query_rag.py
```

This demonstrates:
1. Basic similarity search
2. Table-only search
3. Filtered search by content type
4. Page range search
5. Multi-query RAG pattern
6. Hybrid search (text + tables)
7. Collection statistics

## Common Use Cases

### Use Case 1: Financial Data Extraction

Extract specific financial metrics from tables:
```bash
python src/query_chromadb.py "net interest income components" --tables-only --n-results 5
```

### Use Case 2: Risk Analysis

Find all risk-related sections:
```bash
python src/query_chromadb.py "risk factors credit risk" --content-type section_header
```

### Use Case 3: Multi-Document Search

If you have multiple documents ingested, filter by source:
```python
from query_chromadb import ChromaDBQuerier

querier = ChromaDBQuerier()
results = querier.similarity_search(
    "revenue growth",
    n_results=10,
    where={"source": "10q_3q25.pdf"}
)
```

## Programmatic Usage

### Python Integration

```python
from query_chromadb import ChromaDBQuerier

# Initialize querier
querier = ChromaDBQuerier()

# Basic search
results = querier.similarity_search("credit losses", n_results=5)

# Access results
for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"Page {metadata['page']}: {doc[:100]}...")

# Search with filters
table_results = querier.search_tables_only("financial statements", n_results=3)

# Page range search
page_results = querier.search_by_page_range(
    "risk management",
    page_min=10,
    page_max=20,
    n_results=5
)

# Collection statistics
stats = querier.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")
```

## Configuration Options

### Custom Collection Name

```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --collection my_financial_docs
python src/query_chromadb.py "revenue" --collection my_financial_docs
```

### Filter Content During Ingestion

Ingest only tables:
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --include-types table
```

Exclude images and captions:
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --exclude-types picture,caption
```

### Reset Collection

Clear and re-ingest:
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --reset
```

## Troubleshooting

### Error: Collection not found

Make sure you've run the ingestion script first:
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json
```

### Slow first query

The first query loads the embedding model into memory. Subsequent queries will be faster.

### Out of memory

Reduce batch size during ingestion:
```bash
python src/ingest_to_chromadb.py data/10q_3q25_rag.json --batch-size 50
```

## Next Steps

1. **Integrate with LLM**: Use retrieved contexts with GPT-4, Claude, or other LLMs
2. **Add Re-ranking**: Implement re-ranking for improved retrieval quality
3. **Hybrid Search**: Combine vector search with keyword search
4. **Multi-query**: Decompose complex questions into multiple queries
5. **Fine-tune**: Experiment with different embedding models

## Advanced Configuration

Edit `src/chromadb_config.py` to customize:
- Embedding model
- Batch size
- Persistence directory
- Default number of results
- Collection name

Example:
```python
from chromadb_config import create_custom_config

config = create_custom_config(
    persist_directory="./my_vectordb",
    collection_name="my_docs",
    batch_size=200
)
```
