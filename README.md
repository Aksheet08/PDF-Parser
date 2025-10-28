# PDF Parser - Structured JSON Extraction

A Python application that extracts structured content from PDF files and converts it into well-organized JSON format while preserving document hierarchy.

## Author
**Aksheet Ranjan**  
Email: a.ranjan8104@gmail.com
[LinkedIn](https://www.linkedin.com/in/aksheetranjan/)




## Features

- **Multi-content Detection**: Extracts paragraphs, tables, and charts from PDF documents
- **Hierarchical Structure**: Maintains page-level organization and section/subsection hierarchy
- **Robust Parsing**: Handles various PDF formats and content types
- **Clean Output**: Produces well-structured JSON with metadata and timestamps
- **Modular Design**: Object-oriented architecture for easy extension and maintenance
- **Error Handling**: Comprehensive logging and error management
- **Command Line Interface**: Easy-to-use CLI with flexible options

## Requirements

### System Requirements
- Python 3.7 or higher
- Operating System: Windows, macOS, or Linux

### Python Dependencies
The following libraries are required:

```txt
pdfplumber>=0.7.0
PyMuPDF>=1.23.0
pandas>=1.5.0
pillow>=9.0.0
numpy>=1.21.0
```

## Installation

### 1. Download
Download the `pdf_parser.py` script to your local machine.

### 2. Install Dependencies

#### Option A: Using pip (Recommended)
```bash
pip install pdfplumber PyMuPDF pandas pillow numpy
```

#### Option B: Using requirements.txt
Create a `requirements.txt` file with the dependencies listed above, then run:
```bash
pip install -r requirements.txt
```

#### Option C: Using conda
```bash
conda install -c conda-forge pdfplumber pymupdf pandas pillow numpy
```


## Usage

### Basic Usage
```bash
python pdf_parser.py input_file.pdf
```
This will create an output file named `input_file_extracted.json` in the same directory.

### Advanced Usage

#### Specify Custom Output File
```bash
python pdf_parser.py input_file.pdf -o custom_output.json
```

#### Enable Verbose Logging
```bash
python pdf_parser.py input_file.pdf -v
```

#### Full Command with All Options
```bash
python pdf_parser.py document.pdf --output results.json --verbose
```

### Command Line Arguments

| Argument | Short | Description | Required |
|----------|-------|-------------|----------|
| `pdf_file` | - | Path to input PDF file | Yes |
| `--output` | `-o` | Output JSON file path | No |
| `--verbose` | `-v` | Enable verbose logging | No |


## Output Format

The generated JSON follows this structure:

```json
{
  "pages": [
    {
      "page_number": 1,
      "content": [
        {
          "type": "paragraph",
          "section": "Introduction",
          "sub_section": "Background",
          "text": "Extracted paragraph text..."
        },
        {
          "type": "table",
          "section": "Financial Data",
          "sub_section": null,
          "description": "Table description",
          "table_data": [
            ["Header1", "Header2", "Header3"],
            ["Row1Col1", "Row1Col2", "Row1Col3"],
            ["Row2Col1", "Row2Col2", "Row2Col3"]
          ]
        },
        {
          "type": "chart",
          "section": "Performance Overview",
          "sub_section": null,
          "description": "Chart description",
          "chart_data": [],
          "context_text": "Associated text context"
        }
      ]
    }
  ],
  "metadata": {
    "source_file": "input.pdf",
    "total_pages": 5,
    "extraction_timestamp": "2025-09-18T17:00:00.000000"
  }
}
```

### Content Types

1. **Paragraphs**: Regular text content with section hierarchy
2. **Tables**: Structured tabular data with headers and rows
3. **Charts**: Detected visual elements and chart references

## Examples

### Example 1: Basic PDF Processing
```bash
python pdf_parser.py financial_report.pdf
```
Output: `financial_report_extracted.json`

### Example 2: Research Paper Processing
```bash
python pdf_parser.py research_paper.pdf -o paper_analysis.json -v
```
Output: `paper_analysis.json`

### Example 3: Batch Processing (using shell script)
```bash
for pdf in *.pdf; do
    python pdf_parser.py "$pdf" -o "${pdf%.pdf}_extracted.json"
done
```

## Architecture

### Classes and Methods

#### PDFParser Class
- `__init__(pdf_path)`: Initialize parser with PDF file
- `load_pdf()`: Load PDF document using pdfplumber
- `extract_sections_from_text()`: Parse text for section hierarchy
- `extract_tables()`: Extract and clean table data
- `detect_charts()`: Identify charts and visual elements
- `process_page()`: Process individual page content
- `extract_to_json()`: Main extraction orchestrator
- `save_json()`: Save results to JSON file


## Troubleshooting

### Common Issues

#### 1. "Required library not installed" Error
**Solution**: Install missing dependencies using pip:
```bash
pip install pdfplumber PyMuPDF pandas pillow numpy
```

#### 2. "PDF file not found" Error
**Solution**: Verify the file path and ensure the PDF file exists:
```bash
ls -la your_file.pdf  # On Linux/macOS
dir your_file.pdf     # On Windows
```
-Also try to rename the file to a simpler name without special symbols

#### 3. Permission Denied Error
**Solution**: Check file permissions and run with appropriate privileges:
```bash
chmod +r your_file.pdf  # Make file readable
```

#### 4. Memory Issues with Large PDFs
**Solution**: The script processes pages sequentially to minimize memory usage, but for very large files:
- Close other applications
- Use a machine with more RAM
- Split large PDFs into smaller chunks


### Logging and Debugging

Enable verbose logging to get detailed information:
```bash
python pdf_parser.py document.pdf -v
```

Check the console output for:
- Page processing progress
- Extraction statistics
- Warning messages
- Error details



## Support

For issues or questions:
1. Check the troubleshooting section
2. Ensure all dependencies are properly installed
