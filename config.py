# PDF Parser Configuration
# Advanced configuration options for customizing extraction behavior

import re

class PDFParserConfig:
    """Configuration class for PDF Parser settings"""

    # Section Detection Patterns
    # Add or modify these patterns to improve section detection
    SECTION_PATTERNS = [
        r'^\d+\.\s+([A-Z][^\n]+)$',      # 1. Section Name
        r'^([A-Z][A-Z\s]{3,})$',            # ALL CAPS SECTIONS (min 3 chars)
        r'^([A-Z][a-z\s]+):',               # Title Case:
        r'^\*\*([^\*]+)\*\*',           # **Bold sections**
        r'^##\s+(.+)$',                     # ## Markdown headers
        r'^#\s+(.+)$',                      # # Markdown headers
        r'^([A-Z][a-z\s]+)\n[-=]+$',       # Underlined headers
    ]

    # Chart Detection Keywords
    CHART_KEYWORDS = [
        'chart', 'graph', 'figure', 'diagram', 'plot',
        'visualization', 'illustration', 'image',
        'bar chart', 'pie chart', 'line graph', 'scatter plot'
    ]

    # Table Detection Settings
    TABLE_SETTINGS = {
        'min_rows': 2,              # Minimum rows to consider as table
        'min_cols': 2,              # Minimum columns to consider as table
        'clean_empty_cells': True,  # Remove empty cells
        'strip_whitespace': True,   # Strip whitespace from cells
    }

    # Text Processing Settings
    TEXT_PROCESSING = {
        'min_paragraph_length': 10,     # Minimum characters for paragraph
        'merge_short_lines': True,      # Merge lines shorter than threshold
        'short_line_threshold': 50,     # Threshold for short lines
        'remove_extra_spaces': True,    # Remove multiple spaces
        'preserve_line_breaks': False,  # Keep original line breaks
    }

    # Output Settings
    OUTPUT_SETTINGS = {
        'include_metadata': True,       # Include extraction metadata
        'include_timestamps': True,     # Include processing timestamps
        'pretty_print': True,           # Format JSON with indentation
        'ensure_ascii': False,          # Allow unicode characters
        'indent_size': 2,               # JSON indentation size
    }

    # Logging Settings
    LOGGING = {
        'level': 'INFO',                # DEBUG, INFO, WARNING, ERROR
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'include_page_progress': True,  # Show page processing progress
        'include_extraction_stats': True, # Show extraction statistics
    }

    # Performance Settings
    PERFORMANCE = {
        'max_pages_in_memory': 10,      # Pages to keep in memory
        'enable_caching': False,        # Cache processed pages
        'parallel_processing': False,   # Enable parallel page processing
        'max_workers': 2,               # Number of worker threads
    }

    @classmethod
    def get_section_patterns(cls):
        """Get compiled regex patterns for section detection"""
        return [re.compile(pattern, re.MULTILINE) for pattern in cls.SECTION_PATTERNS]

    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []

        # Validate table settings
        if cls.TABLE_SETTINGS['min_rows'] < 1:
            errors.append("min_rows must be >= 1")
        if cls.TABLE_SETTINGS['min_cols'] < 1:
            errors.append("min_cols must be >= 1")

        # Validate text processing
        if cls.TEXT_PROCESSING['min_paragraph_length'] < 0:
            errors.append("min_paragraph_length must be >= 0")

        # Validate performance settings
        if cls.PERFORMANCE['max_pages_in_memory'] < 1:
            errors.append("max_pages_in_memory must be >= 1")
        if cls.PERFORMANCE['max_workers'] < 1:
            errors.append("max_workers must be >= 1")

        return errors

# Example of how to use custom configuration:
#
# from config import PDFParserConfig
# 
# # Modify settings
# PDFParserConfig.CHART_KEYWORDS.extend(['flowchart', 'network diagram'])
# PDFParserConfig.TABLE_SETTINGS['min_rows'] = 3
# 
# # Validate configuration
# errors = PDFParserConfig.validate_config()
# if errors:
#     print("Configuration errors:", errors)
