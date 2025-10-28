import os
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

try:
    import pdfplumber
    import fitz  # PyMuPDF
    import pandas as pd
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"Required library not installed: {e}")
    print("Please install dependencies")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """
    A robust PDF parser that extracts structured content into JSON format.

    This class handles extraction of paragraphs, tables, and charts while
    maintaining hierarchical document structure.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize the PDF parser with the given PDF file path.

        Args:
            pdf_path (str): Path to the PDF file to be parsed
        """
        self.pdf_path = pdf_path
        self.document = None
        self.extracted_data = {
            "pages": [],
            "metadata": {
                "source_file": os.path.basename(pdf_path),
                "total_pages": 0,
                "extraction_timestamp": None
            }
        }

    def load_pdf(self) -> bool:
        """
        Load the PDF document using pdfplumber.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.document = pdfplumber.open(self.pdf_path)
            self.extracted_data["metadata"]["total_pages"] = len(self.document.pages)
            logger.info(f"Successfully loaded PDF: {self.pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return False

    def extract_sections_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract section and subsection information from text using patterns.

        Args:
            text (str): Input text to analyze

        Returns:
            List[Dict]: List of text segments with section information
        """
        # Common section patterns
        section_patterns = [
            r'^\d+\.\s+([A-Z][^\n]+)$',  # 1. Section Name
            r'^([A-Z][A-Z\s]+)$',           # ALL CAPS SECTIONS
            r'^([A-Z][a-z\s]+):',           # Title Case:
            r'^\*\*([^\*]+)\*\*',       # **Bold sections**
        ]

        lines = text.split('\n')
        segments = []
        current_section = None
        current_subsection = None
        current_text = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            is_section = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # Save previous segment if exists
                    if current_text:
                        segments.append({
                            "type": "paragraph",
                            "section": current_section,
                            "sub_section": current_subsection,
                            "text": " ".join(current_text).strip()
                        })
                        current_text = []

                    # Update section context
                    if pattern == section_patterns[0] or pattern == section_patterns[1]:
                        current_section = match.group(1).strip()
                        current_subsection = None
                    else:
                        current_subsection = match.group(1).strip()

                    is_section = True
                    break

            if not is_section:
                current_text.append(line)

        # Add final segment
        if current_text:
            segments.append({
                "type": "paragraph",
                "section": current_section,
                "sub_section": current_subsection,
                "text": " ".join(current_text).strip()
            })

        return segments if segments else [{
            "type": "paragraph",
            "section": None,
            "sub_section": None,
            "text": text.strip()
        }]

    def extract_tables(self, page) -> List[Dict[str, Any]]:
        """
        Extract tables from a PDF page.

        Args:
            page: pdfplumber page object

        Returns:
            List[Dict]: List of extracted tables with metadata
        """
        tables = []
        try:
            page_tables = page.extract_tables()
            for i, table in enumerate(page_tables):
                if table and len(table) > 0:
                    # Clean table data
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [cell.strip() if cell else "" for cell in row]
                        cleaned_table.append(cleaned_row)

                    tables.append({
                        "type": "table",
                        "section": f"Table {i+1}",
                        "sub_section": None,
                        "description": f"Extracted table with {len(cleaned_table)} rows and {len(cleaned_table[0]) if cleaned_table else 0} columns",
                        "table_data": cleaned_table
                    })
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")

        return tables

    def detect_charts(self, page) -> List[Dict[str, Any]]:
        """
        Detect and extract chart information from a PDF page.

        Args:
            page: pdfplumber page object

        Returns:
            List[Dict]: List of detected charts with metadata
        """
        charts = []
        try:
            # Look for images that might be charts
            if hasattr(page, 'images') and page.images:
                for i, img in enumerate(page.images):
                    # Extract image properties
                    bbox = (img['x0'], img['top'], img['x1'], img['bottom'])

                    # Try to extract text near the image for context
                    nearby_text = page.within_bbox(bbox).extract_text()

                    chart_info = {
                        "type": "chart",
                        "section": f"Chart {i+1}",
                        "sub_section": None,
                        "description": f"Detected chart/image at coordinates {bbox}",
                        "chart_data": [],
                        "context_text": nearby_text[:200] if nearby_text else "No context text found"
                    }
                    charts.append(chart_info)

            # Also look for chart-like patterns in text
            text = page.extract_text()
            if text:
                chart_keywords = ['chart', 'graph', 'figure', 'diagram', 'plot']
                lines = text.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in chart_keywords):
                        charts.append({
                            "type": "chart",
                            "section": "Text-referenced Chart",
                            "sub_section": None,
                            "description": line.strip(),
                            "chart_data": [],
                            "context_text": line.strip()
                        })
                        break

        except Exception as e:
            logger.warning(f"Error detecting charts: {e}")

        return charts

    def process_page(self, page_num: int, page) -> Dict[str, Any]:
        """
        Process a single PDF page and extract all content types.

        Args:
            page_num (int): Page number (1-indexed)
            page: pdfplumber page object

        Returns:
            Dict: Processed page data
        """
        logger.info(f"Processing page {page_num}")

        page_data = {
            "page_number": page_num,
            "content": []
        }

        # Extract text content
        text = page.extract_text()
        if text:
            # Extract structured text with sections
            text_segments = self.extract_sections_from_text(text)
            page_data["content"].extend(text_segments)

        # Extract tables
        tables = self.extract_tables(page)
        page_data["content"].extend(tables)

        # Detect charts
        charts = self.detect_charts(page)
        page_data["content"].extend(charts)

        return page_data

    def extract_to_json(self) -> Dict[str, Any]:
        """
        Extract content from all pages and return structured JSON.

        Returns:
            Dict: Complete extracted data in JSON format
        """
        if not self.load_pdf():
            return {}

        try:
            # Add extraction timestamp
            from datetime import datetime
            self.extracted_data["metadata"]["extraction_timestamp"] = datetime.now().isoformat()

            # Process each page
            for page_num, page in enumerate(self.document.pages, 1):
                page_data = self.process_page(page_num, page)
                self.extracted_data["pages"].append(page_data)

            logger.info(f"Successfully extracted content from {len(self.extracted_data['pages'])} pages")

        except Exception as e:
            logger.error(f"Error during extraction: {e}")
        finally:
            if self.document:
                self.document.close()

        return self.extracted_data

    def save_json(self, output_path: str) -> bool:
        """
        Save extracted data to JSON file.

        Args:
            output_path (str): Path where JSON file will be saved

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON file saved successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            return False

def main():
    """
    Main function to run the PDF parser with command line arguments.
    """
    parser = argparse.ArgumentParser(description="Extract structured content from PDF to JSON")
    parser.add_argument("pdf_file", help="Path to input PDF file")
    parser.add_argument("-o", "--output", help="Output JSON file path (default: input_name.json)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input file
    if not os.path.exists(args.pdf_file):
        logger.error(f"Input PDF file not found: {args.pdf_file}")
        return 1

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base_name = Path(args.pdf_file).stem
        output_path = f"{base_name}_extracted.json"

    # Initialize parser and extract content
    pdf_parser = PDFParser(args.pdf_file)
    extracted_data = pdf_parser.extract_to_json()

    if not extracted_data:
        logger.error("Failed to extract content from PDF")
        return 1

    # Save results
    if pdf_parser.save_json(output_path):
        logger.info(f"Extraction completed successfully!")
        logger.info(f"Input: {args.pdf_file}")
        logger.info(f"Output: {output_path}")
        logger.info(f"Pages processed: {extracted_data['metadata']['total_pages']}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit(main())
