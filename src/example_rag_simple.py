"""
Simplified example of preparing PDF content for RAG.

This shows a minimal approach to extract and chunk PDF content
for use in RAG applications.
"""

import json
from pathlib import Path
from docling.document_converter import DocumentConverter


def prepare_for_rag(pdf_path: str, output_json: str):
    """
    Simple extraction of PDF content for RAG.
    
    Creates chunks with:
    - Text content
    - Page numbers
    - Content type (heading, paragraph, table, etc.)
    """
    # Convert PDF
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    doc = result.document
    
    # Extract chunks
    chunks = []
    
    for idx, item in enumerate(doc.iterate_items()):
        if not item.text or not item.text.strip():
            continue
        
        # Get page number
        page_num = None
        if hasattr(item, 'prov') and item.prov:
            for prov in item.prov:
                if hasattr(prov, 'page_no'):
                    page_num = prov.page_no
                    break
        
        # Create chunk
        chunk = {
            "id": idx,
            "text": item.text.strip(),
            "page": page_num,
            "type": item.label if hasattr(item, 'label') else 'text',
            "source": Path(pdf_path).name
        }
        
        chunks.append(chunk)
    
    # Save
    output = {
        "document": Path(pdf_path).name,
        "total_chunks": len(chunks),
        "chunks": chunks
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Extracted {len(chunks)} chunks from {doc.name}")
    print(f"✓ Saved to {output_json}")
    
    # Show sample
    if chunks:
        print(f"\nSample chunk:")
        sample = chunks[0]
        print(f"  ID: {sample['id']}")
        print(f"  Type: {sample['type']}")
        print(f"  Page: {sample['page']}")
        print(f"  Text: {sample['text'][:100]}...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/example_rag_simple.py <input.pdf> [output.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else "rag_output.json"
    
    prepare_for_rag(pdf_path, output_json)
