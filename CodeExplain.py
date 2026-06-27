import os
import re
from openai import AzureOpenAI
from dotenv import load_dotenv
import sys

load_dotenv(override=True)

# Configuration
endpoint = "https://azureopenaibarry.openai.azure.com/openai/deployments/o4-mini/chat/completions?api-version=2025-01-01-preview"
model_name = "gpt-4.1"
subscription_key = "BoG9ulFULEke4wmfKvxlu62L9QPROJBdWMAIeWm3M3DALq2HTX0aJQQJ99BFACYeBjFXJ3w3AAABACOG4AEr"
api_version = "2024-12-01-preview"

client = AzureOpenAI(api_version=api_version, azure_endpoint=endpoint, api_key=subscription_key)

print("Please ensure that program files are ready in code explain folder! Let's start code explain. Please wait.")

def clean_unicode(text):
    replacements = {
        u'\u2010': '-', u'\u2011': '-', u'\u2012': '-', u'\u2013': '-', u'\u2014': '-',
        u'\u2018': "'", u'\u2019': "'", u'\u2026': '...', u'\u2192': '->'
    }
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    for ch, repl in replacements.items():
        text = text.replace(ch, repl)
    return text

def analyze_code_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = clean_unicode(f.read())

    messages = [
        {"role": "system", "content": "You are a seasoned software development expert on reviewing and explaining the code of RPGLE program in AS400 (i-series)."},
        {"role": "user", "content": f"Analyze the following code and provide a summary:\n\n```\n{code}\n```"}
    ]

    try:
        return client.chat.completions.create(model=model_name, messages=messages).choices[0].message.content
    except Exception as e:
        return f"Error analyzing {filepath}: {e}"

def analyze_folder(folder):
    supported_extensions = ['.RPGLE', '.SQLRPGLE', '.PF', '.docx']
    return {
        f: analyze_code_file(os.path.join(folder, f))
        for f in os.listdir(folder)
        if any(f.upper().endswith(ext) for ext in supported_extensions)
    }

def safe_print(text):
    try:
        sys.stdout.buffer.write((text + '\n').encode('utf-8'))
    except:
        print(f"Error printing.")

def ask_questions(results):
    combined = "\n\n".join([f"--- {f} ---\n{a}" for f, a in results.items()])
    q = input("Please ask question? (type 'exit' to quit): ")
    while q.lower() != 'exit':
        prompt = [
            {"role": "system", "content": "You are a seasoned software development expert on reviewing and explaining the code of RPGLE program in AS400 (i-series)."},
            {"role": "user", "content": f"Based on analyses:\n\n{combined}\n\nQuestion: {q}"}
        ]
        try:
            answer = client.chat.completions.create(model=model_name, messages=prompt).choices[0].message.content
            safe_print(f"Answer: {answer}")
        except:
            safe_print("Error during response.")
        
        # Prompt to save the answer
        save_prompt = input("Would you like to save this answer? (yes/no): ").strip().lower()
        if save_prompt == 'yes':
            filename = input("Enter filename to save the answer: ").strip()
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Question: {q}\nAnswer: {answer}\n")
                print(f"Answer saved to {filename}")
            except Exception as e:
                print(f"Failed to save answer: {e}")

        q = input("Please ask question? (type 'exit' to quit): ")

if __name__ == "__main__":
    # Prompt user for folder path
    folder = input("Enter the path of the folder containing code files (e.g. C:/Users/B495TB/OneDrive - AXA/desktop/RLSCode): ").strip()
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found.")
    else:
        results = analyze_folder(folder)
        ask_questions(results)
