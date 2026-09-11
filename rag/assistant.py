from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
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
- If the user asks in regional languages (e.g., Tamil, Marathi, Bengali, Telugu), reply in that language.
- Keep official scheme and document names (like "PM-KISAN", "Atal Pension Yojana", "Aadhaar Card") clearly recognizable while explaining.

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

class MaxLabhChatbot:
    def __init__(self, kb: SchemeKnowledgeBase):
        self.retriever = kb.get_retriever(k=3)
        # Fast, free-tier Google Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3
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

        return self.chain.invoke({
            "context": context_str,
            "age": citizen_profile.get("age", "Not specified"),
            "occupation": citizen_profile.get("occupation", "Not specified"),
            "annual_income": citizen_profile.get("annual_income", "Not specified"),
            "bundle_names": bundle_names,
            "missing_docs": missing_docs,
            "question": question
        })