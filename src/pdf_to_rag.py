"""
Extract content from PDF and prepare it for RAG (Retrieval Augmented Generation).

This script demonstrates how to:
1. Convert a PDF using Docling
2. Extract text with semantic structure (sections, paragraphs)
3. Create chunks suitable for vector embeddings
4. Include metadata for better retrieval
5. Export in a format ready for ingestion into vector databases

Usage:
    python src/pdf_to_rag.py input.pdf output_chunks.json
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Configure custom HuggingFace cache location (optional)
# Uncomment and set your desired path to store models in a custom location
# os.environ['HF_HOME'] = '/Volumes/Extreme SSD/huggingface'

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for better context preservation.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunks.append(text[start:end].strip())
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks


def extract_rag_chunks(pdf_path: str, chunk_size: int = 1000, overlap: int = 200, include_tables: bool = False) -> List[Dict[str, Any]]:
    """
    Extract content from PDF and prepare chunks for RAG ingestion.
    
    Args:
        pdf_path: Path to the input PDF file
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        include_tables: Whether to enable table structure recognition
        
    Returns:
        List of chunks with text and metadata
    """
    # Initialize converter with table extraction if requested
    if include_tables:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
    else:
        converter = DocumentConverter()
    
    print(f"Converting {pdf_path}...")
    result = converter.convert(pdf_path)
    doc = result.document
    
    chunks = []
    chunk_id = 0
    
    # Process document structure to create meaningful chunks
    for item, level in doc.iterate_items():
        # Get text content - use markdown export for tables and other items without text
        item_text = None
        if hasattr(item, 'text') and item.text:
            item_text = item.text
        elif hasattr(item, 'export_to_markdown'):
            try:
                item_text = item.export_to_markdown(doc)
            except:
                # Skip items that can't be converted to text
                continue
        
        # Skip items without content
        if not item_text or not item_text.strip():
            continue
        
        # Determine content type
        content_type = item.label if hasattr(item, 'label') else 'text'
        
        # Get page number if available
        page_num = None
        if hasattr(item, 'prov') and item.prov:
            for prov in item.prov:
                if hasattr(prov, 'page_no'):
                    page_num = prov.page_no
                    break
        
        # For long content, split into chunks (but keep tables intact)
        if len(item_text) > chunk_size and content_type != 'table':
            text_chunks = chunk_text(item_text, chunk_size, overlap)
            for i, text_chunk in enumerate(text_chunks):
                chunk_id += 1
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": text_chunk,
                    "metadata": {
                        "source": Path(pdf_path).name,
                        "content_type": content_type,
                        "page": page_num,
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                        "is_partial": True
                    }
                })
        else:
            # Keep as single chunk
            chunk_id += 1
            chunks.append({
                "chunk_id": chunk_id,
                "text": item_text.strip(),
                "metadata": {
                    "source": Path(pdf_path).name,
                    "content_type": content_type,
                    "page": page_num,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "is_partial": False
                }
            })
    
    return chunks


def extract_tables_for_rag(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract tables separately with structured data for RAG.
    
    Args:
        pdf_path: Path to the input PDF file
        
    Returns:
        List of table chunks with structured data
    """
    # Configure converter with table extraction enabled
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    result = converter.convert(pdf_path)
    doc = result.document
    
    table_chunks = []
    table_id = 0
    
    for item, level in doc.iterate_items():
        if hasattr(item, 'label') and item.label == 'table':
            table_id += 1
            
            # Get page number
            page_num = None
            if hasattr(item, 'prov') and item.prov:
                for prov in item.prov:
                    if hasattr(prov, 'page_no'):
                        page_num = prov.page_no
                        break
            
            # Extract table as text representation using markdown export
            try:
                table_text = item.export_to_markdown(doc) if hasattr(item, 'export_to_markdown') else str(item)
            except:
                table_text = str(item)
            
            table_chunks.append({
                "chunk_id": f"table_{table_id}",
                "text": table_text,
                "metadata": {
                    "source": Path(pdf_path).name,
                    "content_type": "table",
                    "page": page_num,
                    "table_id": table_id
                }
            })
    
    return table_chunks


def save_rag_output(chunks: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save chunks in a format suitable for RAG ingestion.
    
    Args:
        chunks: List of chunks with text and metadata
        output_path: Path to save the output JSON file
    """
    output = {
        "total_chunks": len(chunks),
        "chunks": chunks
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(chunks)} chunks to {output_path}")


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python src/pdf_to_rag.py <input.pdf> [output_chunks.json] [--chunk-size SIZE] [--overlap SIZE]")
        print("\nOptions:")
        print("  --chunk-size SIZE    Maximum chunk size in characters (default: 1000)")
        print("  --overlap SIZE       Overlap between chunks in characters (default: 200)")
        print("  --include-tables     Extract tables separately")
        print("\nExample:")
        print("  python src/pdf_to_rag.py document.pdf rag_chunks.json --chunk-size 1500 --overlap 300")
        sys.exit(1)
    
    # Parse arguments
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 and not sys.argv[2].startswith('--') else "rag_chunks.json"
    
    chunk_size = 1000
    overlap = 200
    include_tables = False
    
    for i, arg in enumerate(sys.argv):
        if arg == '--chunk-size' and i + 1 < len(sys.argv):
            chunk_size = int(sys.argv[i + 1])
        elif arg == '--overlap' and i + 1 < len(sys.argv):
            overlap = int(sys.argv[i + 1])
        elif arg == '--include-tables':
            include_tables = True
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found")
        sys.exit(1)
    
    print(f"Configuration:")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    print(f"  Include tables: {include_tables}")
    print()
    
    try:
        # Extract content chunks
        chunks = extract_rag_chunks(pdf_path, chunk_size, overlap, include_tables)
        
        # Extract tables if requested
        if include_tables:
            print("\nExtracting tables...")
            table_chunks = extract_tables_for_rag(pdf_path)
            if table_chunks:
                print(f"Found {len(table_chunks)} tables")
                chunks.extend(table_chunks)
        
        # Save output
        save_rag_output(chunks, output_path)
        
        # Print statistics
        print(f"\nStatistics:")
        print(f"  Total chunks: {len(chunks)}")
        
        content_types = {}
        for chunk in chunks:
            ctype = chunk['metadata']['content_type']
            content_types[ctype] = content_types.get(ctype, 0) + 1
        
        print(f"  Content types:")
        for ctype, count in sorted(content_types.items()):
            print(f"    - {ctype}: {count}")
        
        print(f"\n✓ Ready for RAG ingestion!")
        print(f"\nNext steps:")
        print(f"  1. Generate embeddings for each chunk's text")
        print(f"  2. Store in vector database (e.g., Pinecone, Weaviate, ChromaDB)")
        print(f"  3. Use metadata for filtering and retrieval")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
