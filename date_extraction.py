# date_extraction.py

import re
import pdfplumber
from datetime import datetime

def format_metadata_date(metadata_date):
    """Format PDF metadata date into YYYY-MM-DD."""
    try:
        if metadata_date.startswith("D:"):
            metadata_date = metadata_date[2:]  # Remove leading "D:"
        return datetime.strptime(metadata_date[:8], "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return None

def extract_metadata_date(file_path):
    """Extract creation date from PDF metadata (if available)."""
    try:
        if file_path.lower().endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                meta = pdf.metadata
                if meta and "CreationDate" in meta:
                    return format_metadata_date(meta["CreationDate"])
        return None
    except Exception:
        return None

def extract_document_date(text, file_path):
    """
    Extract document date from text patterns (YYYY-MM-DD, etc.).
    Falls back to PDF metadata if not found.
    """
    date_patterns = [
        r"\b(\d{4})[-/](\d{2})[-/](\d{2})\b",
        r"\b(\d{2})[-/](\d{2})[-/](\d{4})\b",
        r"\b(\d{1,2}) (\w+) (\d{4})\b",
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if len(match.groups()) == 3:
                    raw_date = "-".join(match.groups())
                    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                else:
                    raw_date = " ".join(match.groups())
                    parsed_date = datetime.strptime(raw_date, "%d %B %Y")
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

    metadata_date = extract_metadata_date(file_path)
    return metadata_date if metadata_date else "0000-00-00"


