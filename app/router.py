from pydantic import BaseModel

from fastapi import APIRouter
from app.retriever import search_docs, initialize_index
from app.utils import extract_all_documents
from app.rag_chain import generate_answer


class Query(BaseModel):
    user_input: str

router = APIRouter()

@router.get("/initialize")
def initialize():
    initialize_index()
    return {"message": "Index initialized"}

@router.post("/ask")
def ask_question(query: Query):
    user_input = query.user_input
    context = search_docs(user_input)
    answer = generate_answer(user_input, context)
    return {"answer": answer}

@router.get("/test-extract")
def test_extract():
    text = extract_all_documents("data/raw/Insurance PDFs")
    return {"length": len(text), "preview": text[:500]}