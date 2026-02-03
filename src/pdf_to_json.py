"""
Sample Docling program to convert PDF to JSON format.

This script demonstrates how to:
1. Load a PDF file using Docling
2. Convert it to the standard Docling document format
3. Export it as JSON

Usage:
    python src/pdf_to_json.py input.pdf output.json
"""

import os
import sys
import json
from pathlib import Path

# Configure custom HuggingFace cache location (optional)
# Uncomment and set your desired path to store models in a custom location
# os.environ['HF_HOME'] = '/Volumes/Extreme SSD/huggingface'

from docling.document_converter import DocumentConverter


def convert_pdf_to_json(pdf_path: str, output_path: str) -> None:
    """
    Convert a PDF file to Docling JSON format.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path where the JSON output will be saved
    """
    # Initialize the DocumentConverter
    converter = DocumentConverter()
    
    # Convert the PDF document
    print(f"Converting {pdf_path}...")
    result = converter.convert(pdf_path)
    
    # Export to JSON format
    print(f"Exporting to {output_path}...")
    json_output = result.document.export_to_dict()
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Successfully converted {pdf_path} to {output_path}")
    print(f"Document contains {len(result.document.pages)} page(s)")


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python src/pdf_to_json.py <input.pdf> [output.json]")
        print("\nExample:")
        print("  python src/pdf_to_json.py sample.pdf output.json")
        sys.exit(1)
    
    # Get input PDF path
    pdf_path = sys.argv[1]
    
    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"Error: File '{pdf_path}' not found")
        sys.exit(1)
    
    # Determine output path
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Default: same name as input but with .json extension
        output_path = Path(pdf_path).stem + ".json"
    
    # Convert the PDF
    try:
        convert_pdf_to_json(pdf_path, output_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
