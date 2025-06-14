import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.utils import extract_all_documents, save_processed_text
import os
# Inserted for Gemini extraction and file handling
from app.llm_extractor import extract_qae_from_text
import glob
import json

context_chunks = []
embedded_chunks = []

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

embedding_model = genai.embed_content

def initialize_index():
    global context_chunks, embedded_chunks

    raw_folder = "data/raw/Insurance PDFs"
    processed_folder = "data/processed"

    extracted_texts = extract_all_documents(raw_folder)
    for filename, content in extracted_texts.items():
        save_processed_text(content, filename)

    extracted_folder = "data/extracted"

    # Run Gemini extraction if .json not created
    for txt_path in glob.glob(os.path.join(processed_folder, "*.txt")):
        base_filename = os.path.splitext(os.path.basename(txt_path))[0]
        json_path = os.path.join(extracted_folder, f"{base_filename}.json")
        if not os.path.exists(json_path):
            print(f"Processing {txt_path}, saving to {json_path}")
            with open(txt_path, "r", encoding="utf-8") as f:
                text_content = f.read()
            extract_qae_from_text(text_content, base_filename)

    # Load all extracted chunks from .json files
    context_chunks.clear()
    embedded_chunks.clear()
    for path in glob.glob(os.path.join(extracted_folder, "*.json")):
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                context_chunks.append(item)
                try:
                    emb = embedding_model(content=item["chunk"], model="models/embedding-001")['embedding']
                    embedded_chunks.append(emb)
                except Exception as e:
                    print(f"Failed to embed chunk: {e}")

def search_docs(query, top_k=5, similarity_threshold=0.6):
    # Embed query
    query_embedding = embedding_model(content=query, model="models/embedding-001")['embedding']

    if not embedded_chunks:
        return None
    
    # Compute similarity
    sims = cosine_similarity([query_embedding], embedded_chunks)[0]

    max_sim = np.max(sims)
    if max_sim < similarity_threshold:
        return None

    # Get top_k results
    top_indices = np.argsort(sims)[::-1][:top_k]
    top_chunks = [context_chunks[i] for i in top_indices]

    return top_chunks
