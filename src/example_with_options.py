"""
Advanced example showing Docling configuration options.

This demonstrates how to customize the conversion process with
different options for OCR, table extraction, and other features.
"""

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


def advanced_conversion_example(pdf_path: str, output_json: str):
    """
    Example with custom pipeline options.
    
    Args:
        pdf_path: Path to the PDF file to convert
        output_json: Path to save the JSON output
    """
    # Configure pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True  # Enable OCR for scanned documents
    pipeline_options.do_table_structure = True  # Enable table structure recognition
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # Use accurate mode
    
    # Create converter with custom options
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )
    
    print(f"Converting {pdf_path} with advanced options...")
    print(f"- OCR enabled: {pipeline_options.do_ocr}")
    print(f"- Table extraction enabled: {pipeline_options.do_table_structure}")
    
    # Convert the document
    result = converter.convert(pdf_path)
    doc = result.document
    
    # Save as JSON
    import json
    json_output = doc.export_to_dict()
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Conversion complete!")
    print(f"- Pages processed: {len(doc.pages)}")
    print(f"- Output saved to: {output_json}")
    
    # Count tables if any
    tables = [item for item in doc.iterate_items() if item.label == "table"]
    if tables:
        print(f"- Tables found: {len(tables)}")
    
    # Also save as markdown for easy viewing
    markdown_path = output_json.replace('.json', '.md')
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(doc.export_to_markdown())
    print(f"- Markdown saved to: {markdown_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python src/example_with_options.py <input.pdf> [output.json]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else "output_advanced.json"
    
    advanced_conversion_example(pdf_path, output_json)
