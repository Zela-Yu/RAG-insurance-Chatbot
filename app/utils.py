import pdfplumber
import docx
import os
import re

def clean_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'\s*\(.*?\)', '', name)
    return name.strip()

def extract_text_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    save_processed_text(full_text, base_name)
    return full_text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    save_processed_text(text, base_name)
    return text

def save_processed_text(text, filename):
    clean_name = clean_filename(filename)
    os.makedirs("data/processed", exist_ok=True)
    output_path = os.path.join("data/processed", f"{clean_name}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def extract_all_documents(folder_path):
    all_texts = {}
    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(path)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(path)
        else:
            continue
        all_texts[filename] = text
    return all_texts

def split_into_chunks(text, max_chars=500):
    lines = text.split("\n")
    chunks, current_chunk = [], ""
    for line in lines:
        if len(current_chunk) + len(line) < max_chars:
            current_chunk += line + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks