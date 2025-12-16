# agent/document_validator.py

from typing import Dict
import json
import re
import os

from dotenv import load_dotenv
load_dotenv()

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

from agent.system_prompt import DOCUMENT_VALIDATION_SYSTEM_PROMPT

# ------------------------------------------------------------------
# ENV CHECK (remove print after debugging)
# ------------------------------------------------------------------

print("GOOGLE_API_KEY loaded:", bool(os.getenv("GOOGLE_API_KEY")))

# ------------------------------------------------------------------
# LLM (Gemini)
# ------------------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0
)

# ------------------------------------------------------------------
# TOOL: Document Validation
# ------------------------------------------------------------------

@tool
def validate_uploaded_document(
    task_name: str,
    file_name: str,
    file_extension: str
) -> Dict:
    """
    Validate whether the uploaded document matches the expected task.

    MUST return JSON:
    {
      "accepted": true/false,
      "reason": "short explanation"
    }
    """

    # Check file format
    if file_extension not in ["pdf", "jpg", "jpeg", "png"]:
        return {
            "accepted": False,
            "reason": "Unsupported file format"
        }

    # Basic filename-to-task relevance check
    task_keywords = task_name.lower().replace("upload", "").strip().split()
    filename_lower = file_name.lower()

    if not any(keyword in filename_lower for keyword in task_keywords):
        return {
            "accepted": False,
            "reason": "Filename does not match expected document"
        }

    return {
        "accepted": True,
        "reason": "File format and filename match expected document"
    }

# ------------------------------------------------------------------
# REACT AGENT
# ------------------------------------------------------------------

document_validation_agent = create_react_agent(
    model=llm,
    tools=[validate_uploaded_document]
)

# ------------------------------------------------------------------
# PUBLIC FUNCTION CALLED BY UI
# ------------------------------------------------------------------

def run_document_validation_agent(
    task_name: str,
    file_name: str
) -> Dict:
    """
    Runs the document validation agent and returns a structured decision.
    """

    file_extension = file_name.split(".")[-1].lower()

    response = document_validation_agent.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": DOCUMENT_VALIDATION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"""
Task: {task_name}
File name: {file_name}
File extension: {file_extension}

Validate whether this document satisfies the task.
"""
                }
            ]
        }
    )

    # Extract final message
    final_message = response["messages"][-1].content

    # Robust JSON extraction (Gemini-safe)
    try:
        json_str = re.search(r"\{.*\}", final_message, re.DOTALL).group()
        return json.loads(json_str)
    except Exception:
        return {
            "accepted": False,
            "reason": "Invalid agent response format"
        }
