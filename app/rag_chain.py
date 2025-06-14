import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_answer(query, context_chunks):
    if not context_chunks:
        return "I don't know."
    
    structured_context = "\n".join([
        f"- Plan: {entry['plan']}\n  Topic: {entry['topic']}\n  Content: {entry['chunk']}"
        for entry in context_chunks
    ])

    prompt = (
        f"You are a helpful support assistant for an insurance company.\n\n"
        f"The provided context consists of multiple entries. Each entry includes:\n"
        f"- the insurance plan name under 'plan',\n"
        f"- a topic keyword under 'topic', and\n"
        f"- a factual description under 'content'.\n\n"
        f"The known plan names are:\n"
        f"- America's Choice 2500 Gold SOB\n"
        f"- America's Choice 5000 Bronze SOB\n"
        f"- America's Choice 5000 HSA SOB\n"
        f"- America's Choice 7350 Copper SOB\n\n"
        f"When answering a question, match the plan name from context entries to the user question in a flexible way (case-insensitive, partial match allowed), as long as the reference is clear.\n\n"
        f"Context entries:\n{structured_context}\n\n"
        f"User question: {query}\n"
        f"Answer:"
    )
    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini Error] {e}"