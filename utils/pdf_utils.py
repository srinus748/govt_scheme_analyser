# utils/pdf_utils.py

import PyPDF2
from fpdf import FPDF
import hashlib
import datetime
import os
from io import BytesIO

def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text from an uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return "Error: Could not read the PDF file. It might be corrupted or password-protected."

def create_summary_pdf(summary_en: str, summary_te: str, shared_dir: str) -> str:
    """
    Generates a PDF with English and Telugu summaries using Unicode fonts.
    Returns the path to the saved PDF.
    """
    # Ensure the shared directory exists
    os.makedirs(shared_dir, exist_ok=True)
    
    # Create a unique filename
    content_hash = hashlib.sha256((summary_en + summary_te).encode()).hexdigest()[:16]
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"summary-{content_hash}-{timestamp}.pdf"
    filepath = os.path.join(shared_dir, filename)

    # --- PDF Generation ---
    class PDF(FPDF):
        def header(self):
            # This will now work because the font is already registered
            self.set_font('Unicode', '', 18) 
            self.cell(0, 10, 'AI-Sahayak: Scheme Summary', 0, 1, 'C')
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Unicode', '', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()

    # --- REGISTER FONTS IMMEDIATELY ---
    # This is the crucial fix. Fonts must be added before add_page() is called.
    
    # English Unicode Font
    unicode_font_path = os.path.join("fonts", "DejaVuSans.ttf")
    if os.path.exists(unicode_font_path):
        pdf.add_font('Unicode', '', unicode_font_path, uni=True)
    else:
        print(f"WARNING: DejaVuSans.ttf not found at {unicode_font_path}. PDF may not render correctly.")

    # Telugu Unicode Font
    telugu_font_path = os.path.join("fonts", "NotoSansTelugu-Regular.ttf")
    if os.path.exists(telugu_font_path):
        pdf.add_font('Telugu', '', telugu_font_path, uni=True)
    else:
        print(f"WARNING: NotoSansTelugu-Regular.ttf not found at {telugu_font_path}. PDF may not render correctly.")

    # Now that fonts are registered, we can add the page.
    # The header() and footer() methods will be able to find the 'Unicode' font.
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add English section
    pdf.set_font('Unicode', '', 14)
    pdf.cell(0, 10, 'English Summary', 0, 1, 'L')
    pdf.set_font('Unicode', '', 11)
    pdf.multi_cell(0, 8, summary_en)
    pdf.ln(10)

    # Add Telugu section
    if os.path.exists(telugu_font_path):
        pdf.set_font('Telugu', '', 14)
        pdf.cell(0, 10, 'తెలుగు సారాంశం (Telugu Summary)', 0, 1, 'L')
        pdf.set_font('Telugu', '', 11)
        pdf.multi_cell(0, 8, summary_te)
    else:
        # Fallback for Telugu if font is missing
        pdf.set_font('Unicode', '', 12)
        pdf.cell(0, 10, 'Telugu Summary (Font Not Found)', 0, 1, 'L')
        pdf.set_font('Unicode', '', 11)
        pdf.multi_cell(0, 8, "Telugu font (NotoSansTelugu-Regular.ttf) not found in /fonts directory. Displaying plain text.")
        pdf.multi_cell(0, 8, summary_te)

    try:
        pdf.output(filepath)
        return filepath
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None