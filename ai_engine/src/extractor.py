import pymupdf  # PyMuPDF
import re
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class TextExtractor:
    """Extracts and cleans raw text from PDF Resumes."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Reads a PDF file and extracts raw text page by page."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = pymupdf.open(pdf_path)
        full_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            full_text.append(text)
            
        return "\n".join(full_text)

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Cleans and normalizes extracted resume text."""
        if not raw_text:
            return ""
            
        # 1. Normalize line endings
        text = re.sub(r'\r\n|\r|\n', '\n', raw_text)
        
        # 2. Replace weird bullet symbols with standard hyphens
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u25C6\u25AA\u25FE\u2026\u2013\u2014]', '-', text)
        
        # 3. Consolidate multiple spaces and tabs into single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 4. Remove empty or trailing whitespace lines
        cleaned_lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(cleaned_lines)

    @classmethod
    def process_resume(cls, pdf_path: str) -> dict:
        """Extracts and cleans resume text, returning structured metadata."""
        raw_text = cls.extract_text_from_pdf(pdf_path)
        cleaned_text = cls.clean_text(raw_text)
        
        return {
            "file_name": os.path.basename(pdf_path),
            "character_count": len(cleaned_text),
            "line_count": len(cleaned_text.split('\n')),
            "raw_text": raw_text,
            "cleaned_text": cleaned_text
        }


def create_sample_pdf(output_path: str):
    """Creates a sample PDF resume for testing PyMuPDF extractor."""
    doc = pymupdf.open()
    page = doc.new_page()
    
    sample_cv_content = """John Doe
Email: john.doe@example.com | Phone: +1-555-0199
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

SUMMARY
Experienced Software Engineer with 3+ years in Python, SQL, and Cloud Architecture.

SKILLS
- Languages: Python, SQL, JavaScript, HTML/CSS
- Databases: PostgreSQL, MySQL, Redis
- Cloud & DevOps: AWS, Docker, Git, CI/CD Pipelines
- Frameworks: FastAPI, React.js, Pandas

EXPERIENCE
Software Engineer | ABC Tech | 2023 - Present
- Built scalable RESTful APIs using FastAPI and PostgreSQL.
- Implemented automated CI/CD pipelines reducing deployment time by 40%.

Junior Developer | XYZ Solutions | 2022 - 2023
- Developed database schemas and optimized SQL queries.
- Created interactive dashboards using React.js.

EDUCATION
Bachelor of Science in Computer Science | State University (2018 - 2022)
"""
    
    rect = pymupdf.Rect(50, 50, 550, 750)
    page.insert_textbox(rect, sample_cv_content, fontsize=11)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()


if __name__ == "__main__":
    sample_pdf_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_cvs", "sample_resume.pdf")
    create_sample_pdf(sample_pdf_path)
    
    print("\n--- Testing TextExtractor ---")
    result = TextExtractor.process_resume(sample_pdf_path)
    
    print(f"File: {result['file_name']}")
    print(f"Extracted Characters: {result['character_count']}")
    print(f"Extracted Lines: {result['line_count']}")
    print("\nFirst 300 Characters Preview:")
    print("-" * 40)
    print(result['cleaned_text'][:300])
    print("-" * 40)
