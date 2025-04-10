from flask import Flask, render_template, request, jsonify
import spacy
import pandas as pd
from flask import send_file
import pdfplumber
import os
import easyocr
from PIL import Image
import fitz  # PyMuPDF for PDF to image conversion

app = Flask(__name__, template_folder='templates', static_folder='static')

nlp = spacy.load('en_core_web_trf')
os.makedirs('uploads', exist_ok=True)
reader = easyocr.Reader(['en'])

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
            else:
                # Perform OCR using EasyOCR if text extraction fails
                text += extract_text_from_scanned_pdf(pdf_path, pdf.pages.index(page)) + "\n"
    return text

def extract_text_from_scanned_pdf(pdf_path, page_number):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number)
    image = page.get_pixmap()
    image_path = f"{pdf_path}_page_{page_number}.png"
    image.save(image_path)
    result = reader.readtext(image_path, detail=0)
    pdf_document.close()
    return ' '.join(result)

def extract_text_from_image(image_path):
    result = reader.readtext(image_path, detail=0)
    return ' '.join(result)

def perform_ner(file_path):
    text = ""
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(file_path)
    else:
        return {"error": "Unsupported file format. Please upload PDF or image files."}
    
    if not text.strip():
        return {"error": "No text extracted. Please upload a valid file."}

    doc = nlp(text)
    
    # Use a set to store unique (entity text, label) pairs
    unique_entities = list(set((ent.text.strip(), ent.label_) for ent in doc.ents if ent.text.strip()))
    
    return unique_entities



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    entities = perform_ner(file_path)
    return jsonify(entities)

@app.route('/download_excel', methods=['POST'])
def download_excel():
    data = request.get_json()
    entities = data.get('entities', [])
    
    # Convert to DataFrame
    df = pd.DataFrame(entities, columns=['Entity', 'Label'])

    # Save to Excel
    excel_path = 'uploads/entities.xlsx'
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
