from pypdf import PdfReader
from pathlib import Path
import sys

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

if __name__ == "__main__":
    evidence_dir = Path("04-Evidence-Archive")
    output_dir = Path("extracted_text")
    output_dir.mkdir(exist_ok=True)
    
    for pdf_file in evidence_dir.glob("*.pdf"):
        try:
            text = extract_text_from_pdf(pdf_file)
            output_file = output_dir / f"{pdf_file.stem}.txt"
            output_file.write_text(text, encoding="utf-8")
            print(f"Extracted: {pdf_file.name} -> {output_file.name} ({len(text)} chars)")
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
    
    print(f"\nAll PDFs processed. Text files saved to {output_dir}/")
    print("Ready for the reunification evidence dossier.")
