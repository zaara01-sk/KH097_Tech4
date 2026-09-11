import json
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class SchemeKnowledgeBase:
    def __init__(self, data_path: str = "data/schemes_data.json"):
        self.data_path = data_path
        # Google's free-tier text embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.vector_store = self._build_index()

    def _build_index(self) -> FAISS:
        with open(self.data_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)

        docs: List[Document] = []
        for s in schemes:
            content = f"""Scheme Name: {s['name']} (ID: {s['id']})
Category: {s['category']}
Benefit Type: {s['benefit_type']}
Annual Monetary Benefit: ₹{s['annual_benefit_inr']} per year
Official Description: {s['description']}

Eligibility Criteria:
- Minimum Age: {s.get('eligibility', {}).get('min_age', 'None')}
- Maximum Age: {s.get('eligibility', {}).get('max_age', 'None')}
- Income Ceiling: ₹{s.get('eligibility', {}).get('max_annual_income', 'No limit')}
- Target Occupations: {', '.join(s.get('eligibility', {}).get('occupations', ['All']))}
- Requires Agricultural Land: {s.get('eligibility', {}).get('owns_land', False)}
- Disqualifying Conditions: Taxpayer={s.get('eligibility', {}).get('taxpayer', 'N/A')}, EPFO/ESIC={s.get('eligibility', {}).get('enrolled_in_epfo_esic', 'N/A')}

Statutory Conflicts / Mutual Exclusions: {', '.join(s.get('conflicts_with', [])) if s.get('conflicts_with') else 'None'}
Required Documentation: {', '.join(s.get('required_docs', []))}
"""
            docs.append(Document(page_content=content, metadata={"scheme_id": s["id"], "name": s["name"]}))

        return FAISS.from_documents(docs, self.embeddings)

    def get_retriever(self, k: int = 3):
        return self.vector_store.as_retriever(search_kwargs={"k": k})