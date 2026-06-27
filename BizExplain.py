import os
import sys
from openai import OpenAI
import PyPDF2
from docx import Document
import pandas as pd

# Azure OpenAI configuration with your API key
endpoint = "https://barry-mo5ybrmx-eastus2.cognitiveservices.azure.com/openai/v1"
deployment_name = "gpt-5.4-mini"
api_key = "AOh4I2kHRqXhPUJqETvBzLusWnuJn18pA1BxaM0DqmeGtEvZSr3UJQQJ99CDACHYHv6XJ3w3AAAAACOG0VQg"

# Initialize OpenAI client
client = OpenAI(base_url=endpoint, api_key=api_key)

def read_file(filepath):
    """Read file content depending on the file type."""
    if filepath.endswith('.pdf'):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text
    elif filepath.endswith('.docx'):
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
        return df.to_string()
    elif filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
        return df.to_string()
    else:
        return ""  # Unsupported format

def analyze_code_file(filepath):
    """Analyze the content of a file using Azure OpenAI."""
    content = read_file(filepath)
    if not content:
        return "No content to analyze."

    prompt_messages = [
        {"role": "system", "content": "You are a helpful document analysis assistant."},
        {"role": "user", "content": f"Analyze the following content and provide a summary of its functionality:\n\n```\n{content}\n```"}
    ]

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=prompt_messages
        )
        return response.choices[0].message.content if response.choices else "No response."
    except Exception as e:
        return f"Error analyzing {filepath}: {e}"

def analyze_folder(folder_path):
    """Recursively analyze supported files in folder and subfolders."""
    analysis_results = {}
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(('.pdf', '.docx', '.csv', '.xlsx')):
                filepath = os.path.join(root, filename)
                print(f"Analyzing {filepath}...")
                analysis = analyze_code_file(filepath)
                analysis_results[filepath] = analysis
    return analysis_results

def safe_print(text):
    """Safely print text."""
    try:
        sys.stdout.buffer.write((text + '\n').encode('utf-8'))
    except Exception:
        print(text)

def ask_question(analysis_results):
    """Interactively ask questions based on the analysis results."""
    combined_analysis = "\n\n".join(
        [f"--- Analysis for {filepath} ---\n{analysis}" for filepath, analysis in analysis_results.items()]
    )

    while True:
        question = input("Enter your question about the analyses (or type 'exit'): ").strip()
        if question.lower() == 'exit':
            break

        prompt_messages = [
            {"role": "system", "content": "You are a helpful assistant for document analysis."},
            {"role": "user", "content": f"Based on the following analyses, please answer the question:\n\n{combined_analysis}\n\nQuestion: {question}"}
        ]

        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=prompt_messages
            )
            answer = response.choices[0].message.content if response.choices else "No answer."
            safe_print(f"Answer: {answer}")
        except Exception as e:
            safe_print(f"Error: {e}")

if __name__ == "__main__":
    target_folder = r"C:\Users\B495TB\OneDrive - AXA\desktop\TS"  # Replace with your folder path
    if not os.path.exists(target_folder):
        print(f"Folder '{target_folder}' not found. Please create it and add some supported files.")
    else:
        results = analyze_folder(target_folder)
        ask_question(results)