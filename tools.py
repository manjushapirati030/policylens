
import os
import ollama
from pypdf import PdfReader

MODEL_NAME = "gemma"

def load_system_instructions() -> str:
    """Load system instructions from SKILL.md."""
    try:
        with open("SKILL.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are PolicyLens AI, an expert insurance document analyst."

def extract_policy_text(uploaded_file) -> str:
    """Extract text from an uploaded PDF or TXT file."""
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8")
    
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def ask_policy_question(policy_text: str, question: str) -> str:
    """Send policy context and user question to the local Ollama model."""
    system_prompt = load_system_instructions()
    
    prompt = f"""
--- POLICY DOCUMENT ---
{policy_text}

--- USER QUESTION / REQUEST ---
{question}
"""

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running (`ollama run gemma`)."

def generate_policy_summary(policy_text: str) -> str:
    """Generate a summary checklist of coverages, exclusions, and conditions."""
    summary_prompt = (
        "Analyze this policy and provide a structured breakdown containing:\n"
        "1. Key Coverages\n"
        "2. Major Exclusions\n"
        "3. Waiting Periods and Conditions\n"
        "4. Ambiguities or items requiring insurer confirmation."
    )
    return ask_policy_question(policy_text, summary_prompt)