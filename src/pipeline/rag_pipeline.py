from typing import Dict, Any
from rag.assistant import MaxLabhChatbot
from rag.vector_store import SchemeKnowledgeBase

class RAGPipeline:
    def __init__(self, data_path: str = "data/schemes_data.json"):
        self.kb = SchemeKnowledgeBase(data_path=data_path)
        self.assistant = MaxLabhChatbot(self.kb)

    def ask(
        self,
        question: str,
        evaluation_state: Dict[str, Any],
        citizen_profile: Dict[str, Any]
    ) -> str:
        return self.assistant.answer_query(
            question=question,
            evaluation_state=evaluation_state,
            citizen_profile=citizen_profile
        )