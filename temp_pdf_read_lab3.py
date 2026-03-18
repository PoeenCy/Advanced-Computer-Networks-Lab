import fitz
import sys

try:
    doc = fitz.open(r"d:\Advanced-Computer-Networks-Lab\Lab3_Network_Hardening\Lab3_Network_Hardening.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open(r"d:\Advanced-Computer-Networks-Lab\temp_pdf_extracted.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("PDF extraction successful.")
except Exception as e:
    print(f"Error: {e}")
