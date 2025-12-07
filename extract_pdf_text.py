#!/usr/bin/env python3
"""
PDF Text Extractor
Extracts text from PDF files for documentation purposes.

Usage:
    python3 extract_pdf_text.py <pdf_file> [output_file]
    
Examples:
    # Extract to console
    python3 extract_pdf_text.py "Integration docs/Septentrio GPS/rxtools_v25.0.0_user_manual.pdf"
    
    # Extract to file
    python3 extract_pdf_text.py "Integration docs/Septentrio GPS/rxtools_v25.0.0_user_manual.pdf" extracted_text.txt
"""

import sys
import os

try:
    import PyPDF2
except ImportError:
    print("ERROR: PyPDF2 not installed")
    print()
    print("Install with:")
    print("  pip install PyPDF2")
    print()
    sys.exit(1)


def extract_pdf_text(pdf_path, output_path=None):
    """Extract text from PDF file"""
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        return 1
    
    print(f"Extracting text from: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
    print()
    
    try:
        # Open PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"Total pages: {num_pages}")
            print("Extracting text...")
            print()
            
            # Extract text from all pages
            all_text = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                if text.strip():
                    all_text.append(f"--- Page {page_num + 1} ---\n{text}\n")
                
                # Progress indicator
                if (page_num + 1) % 10 == 0:
                    print(f"  Processed {page_num + 1}/{num_pages} pages...")
            
            full_text = '\n'.join(all_text)
            
            # Output
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as out:
                    out.write(full_text)
                print()
                print(f"✓ Text extracted to: {output_path}")
                print(f"  Characters: {len(full_text):,}")
                print(f"  Lines: {full_text.count(chr(10)):,}")
            else:
                print()
                print("=" * 70)
                print(full_text)
                print("=" * 70)
            
            return 0
            
    except Exception as e:
        print(f"ERROR: Failed to extract text")
        print(f"  {type(e).__name__}: {str(e)}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    sys.exit(extract_pdf_text(pdf_file, output_file))
