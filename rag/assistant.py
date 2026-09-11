import os
from typing import Dict, Any
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import SchemeKnowledgeBase

SYSTEM_PROMPT = """You are "MaxLabh Sahayak", an expert public policy and citizen welfare advisor.
Your mission is to help citizens understand Indian government welfare schemes, entitlements, documentation requirements, and conflict-resolution rules.

### CRITICAL LANGUAGE INSTRUCTION:
- Always detect and respond in the EXACT SAME LANGUAGE and SCRIPT/STYLE used by the user in their prompt.
- If the user asks in Hinglish (e.g., "kya main iss scheme ke liye eligible hu?"), reply in natural, fluent Hinglish.
- If the user asks in Hindi script (Devanagari), reply in Hindi (Devanagari).
- If the user asks in English, reply in English.
- If the user asks in regional languages, reply in that language.
- Keep official scheme and document names (like "PM-KISAN", "Atal Pension Yojana", "Aadhaar Card") recognizable.

### GROUNDING RULES:
1. Ground your answers strictly in the provided Scheme Knowledge Context and Citizen Profile Context.
2. If two schemes conflict, explain clearly why one was chosen over the other and the utility difference.
3. State all monetary values in Indian Rupees (₹).
4. Do not invent benefits or criteria not in the context.

--- Scheme Knowledge Context ---
{context}

--- Current Citizen Evaluation Context ---
- Age: {age}
- Occupation: {occupation}
- Annual Family Income: ₹{annual_income}
- Currently Optimal Bundle Recommended by Engine: {bundle_names}
- Missing Required Documents: {missing_docs}
"""

def detect_available_groq_model(api_key: str) -> str:
    """Finds an active working model ID on your Groq key so it never 404s."""
    preferred_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b"
    ]
    try:
        client = Groq(api_key=api_key)
        active_models = [m.id for m in client.models.list().data]
        for preferred in preferred_models:
            if preferred in active_models:
                return preferred
        return active_models[0] if active_models else "llama-3.1-8b-instant"
    except Exception:
        return "llama-3.1-8b-instant"

class MaxLabhChatbot:
    def __init__(self, kb: SchemeKnowledgeBase):
        self.retriever = kb.get_retriever(k=3)
        api_key = os.environ.get("GROQ_API_KEY", "")

        selected_model = detect_available_groq_model(api_key)

        self.llm = ChatGroq(
            model=selected_model,
            temperature=0.2,
            api_key=api_key
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def answer_query(self, question: str, evaluation_state: Dict[str, Any], citizen_profile: Dict[str, Any]) -> str:
        retrieved_docs = self.retriever.invoke(question)
        context_str = "\n\n".join([doc.page_content for doc in retrieved_docs])

        bundle = evaluation_state.get("selected_bundle", [])
        bundle_names = ", ".join([s["name"] for s in bundle]) if bundle else "None"
        missing_docs = ", ".join(evaluation_state.get("doc_metrics", {}).get("missing", [])) or "None"

        try:
            return self.chain.invoke({
                "context": context_str,
                "age": citizen_profile.get("age", "Not specified"),
                "occupation": citizen_profile.get("occupation", "Not specified"),
                "annual_income": citizen_profile.get("annual_income", "Not specified"),
                "bundle_names": bundle_names,
                "missing_docs": missing_docs,
                "question": question
            })
        except Exception as e:
            return (
                f"MaxLabh Sahayak Notice: Encountered API response issue ({str(e)}).\n\n"
                f"**Engine Details:**\n"
                f"- **Recommended Bundle:** {bundle_names}\n"
                f"- **Pending Documents:** {missing_docs}"
            )