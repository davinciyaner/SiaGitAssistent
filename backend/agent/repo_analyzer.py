import os
import json

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from backend.services.git_service import clone_repo

load_dotenv()

# OpenAI Client initialisieren
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def read_files_for_ai(repo_path: str, max_files: int = 10, max_chars: int = 2000):
    """
    Liest die wichtigsten Dateien eines Repos ein, begrenzt auf max_files Dateien
    und max_chars pro Datei, um den Prompt klein zu halten.
    """
    content = []
    for root, dirs, files in os.walk(repo_path):
        for file in files[:max_files]:
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    snippet = f.read(max_chars)
                    content.append(f"File: {path}\n{snippet}\n---")
            except Exception:
                continue
    return "\n".join(content)


def ai_analyze_repo(repo_url: str):
    try:
        repo_path = clone_repo(repo_url)
        repo_text = read_files_for_ai(repo_path)

        prompt = f"""
Du bist ein DevOps AI Agent.
Analysiere dieses GitHub Repository und liefere:
1. genutzte Technologien / Frameworks
2. Projektstruktur
3. CI/CD Workflows
4. Docker Setup
5. Empfohlene nächste Schritte für DevOps

WICHTIG: Antworte **nur** mit gültigem JSON, keine zusätzliche Erklärung.

Repository Inhalt:
{repo_text}
"""

        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        ai_output = response.choices[0].message.content  # <-- wichtig!

        # JSON parsen
        try:
            data = json.loads(ai_output)
        except json.JSONDecodeError:
            data = {"error": "AI output konnte nicht geparst werden", "raw": ai_output}

        return data

    except OpenAIError as e:
        return {"error": "OpenAI API Fehler", "details": str(e)}

    except Exception as e:
        return {"error": "Unerwarteter Fehler", "details": str(e)}