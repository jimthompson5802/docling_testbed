"""
Basic example showing Docling's core functionality.

This demonstrates the simplest way to use Docling to convert a PDF
and access the extracted content.
"""

from docling.document_converter import DocumentConverter


def basic_conversion_example(pdf_path: str):
    """
    Basic example of PDF conversion with Docling.
    
    Args:
        pdf_path: Path to the PDF file to convert
    """
    # Create converter instance
    converter = DocumentConverter()
    
    # Convert the document
    result = converter.convert(pdf_path)
    
    # Access the document
    doc = result.document
    
    # Print basic information
    print(f"Title: {doc.name}")
    print(f"Pages: {len(doc.pages)}")
    print("\n" + "="*50)
    print("Document Content (Markdown):")
    print("="*50)
    
    # Export as markdown (human-readable format)
    markdown = doc.export_to_markdown()
    print(markdown)
    
    # You can also access structured elements
    print("\n" + "="*50)
    print("Structured Elements:")
    print("="*50)
    
    for item in doc.iterate_items():
        print(f"- {item.label}: {item.text[:100]}..." if len(item.text) > 100 else f"- {item.label}: {item.text}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/example_basic.py <input.pdf>")
        sys.exit(1)
    
    basic_conversion_example(sys.argv[1])
