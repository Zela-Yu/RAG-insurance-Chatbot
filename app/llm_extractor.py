import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def extract_qae_from_text(text: str, filename: str):
    # Derive plan name from filename
    import re
    plan_name = re.sub(r"\(\s*\d+\s*\)", "", filename)
    plan_name = re.sub(r"[_\-\(\)]", " ", plan_name) 
    plan_name = re.sub(r"\s+", " ", plan_name).strip()
    plan_name = re.sub(r"\.txt$|\.pdf$|\.processed$|\.json$", "", plan_name, flags=re.IGNORECASE).strip()
    plan_name = plan_name.title()

    # Check for general rules or medical questions content
    if re.search(r"medical|question|eligibility|rules", plan_name, re.IGNORECASE):
        plan_name = "America's Choice Plans (General Rules)"
    
    prompt = f"""
    You are given a document that describes the insurance plan called '{plan_name}'.

    Please extract key information from the document in the following JSON format:
    [
      {{
        "plan": "{plan_name}",
        "chunk": "<natural language description>",
        "topic": "<topic such as deductible, coverage, price, exclusion>"
      }},
      ...
    ]

    TEXT:
    {text}
    """

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        import re

        # Extract the first JSON array block from the response
        json_match = re.search(r"(\[\s*{.*?}\s*\])", raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(1)
        else:
            raise ValueError("No valid JSON array found in response.")
        if not raw_text:
            raise ValueError("Response is empty.")
        data = json.loads(raw_text)
    except Exception as e:
        print(f"Gemini extract_qae_from_text failed: {e}")
        data = []

    # Save to data/extracted as the new processed data
    os.makedirs("data/extracted", exist_ok=True)
    with open(f"data/extracted/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Extracted {len(data)} QAE entries for {plan_name}")
