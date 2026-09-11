# MaxLabh — Autonomous Scheme-Bundle Optimizer 🏹

MaxLabh is a Streamlit app that helps a citizen figure out which Indian government welfare schemes they qualify for, resolves conflicts between mutually-exclusive schemes, and recommends the **maximum-value, non-conflicting bundle** of benefits — combined with a multilingual RAG chatbot ("Sahayak") for follow-up questions.

## Features

- **Deterministic eligibility engine** — checks each scheme's rules (age, income, occupation, land ownership, tax status, EPFO/ESIC enrollment, house ownership, etc.) against a citizen profile.
- **Conflict detection** — flags schemes that are mutually exclusive with one another.
- **Combinatorial bundle optimization** — searches all non-conflicting subsets of eligible schemes to find the one with the highest total annual benefit.
- **Document readiness tracker** — compares documents required by the selected bundle against documents the citizen already holds, and reports a readiness percentage.
- **Full eligibility audit trail** — shows why each scheme was accepted or rejected.
- **Ask Sahayak (AI Advisor)** — a Retrieval-Augmented Generation chatbot (FAISS + HuggingFace embeddings + Groq LLM via LangChain) that answers questions about schemes in whichever language/script the user asks in (English, Hindi, Hinglish, etc.), grounded in the scheme data and the citizen's current evaluation results.

## Architecture

```
app.py                 Streamlit entry point — wires sidebar input → pipelines → tabbed UI
core/
  engine.py            SchemeEngine: eligibility checks, conflict detection, bundle optimization, doc readiness
  models.py             TypedDicts for CitizenProfile, Scheme, EligibilityCriteria
pipeline/
  optimizer.py          OptimizationPipeline: orchestrates the SchemeEngine end-to-end
  rag_pipeline.py        RAGPipeline: builds the knowledge base + chatbot
rag/
  vector_store.py        SchemeKnowledgeBase: builds a FAISS index over scheme descriptions
  assistant.py            MaxLabhChatbot: Groq-backed LangChain chain with a language-mirroring system prompt
ui/
  sidebar.py              Citizen profile input form
  views.py                 Tab renderers (bundle, conflicts, documents, audit trail)
  chatbot_view.py           Chat UI for Ask Sahayak
  styles.py                 Custom CSS
data/
  schemes_data.json         Scheme definitions (eligibility rules, benefits, conflicts, required docs)
docs/                        Architecture diagram & project documentation
```

See `docs/architecture.png` and `docs/KH097_Documentation.pdf` for more detail.

## How it works

1. The sidebar collects a citizen profile (age, occupation, income, land/tax/house/EPFO status, held documents).
2. `SchemeEngine.evaluate_eligibility` checks the profile against every scheme in `data/schemes_data.json` and splits schemes into eligible/ineligible (with reasons).
3. `SchemeEngine.detect_conflicts` finds pairs of eligible schemes that are mutually exclusive.
4. `SchemeEngine.optimize_bundle` performs a combinatorial search over all conflict-free subsets of eligible schemes to select the subset with the highest total `annual_benefit_inr`.
5. `SchemeEngine.generate_document_readiness` computes which required documents are already available vs. missing.
6. The results feed both the dashboard tabs and the RAG chatbot, which grounds its answers in the retrieved scheme context plus the citizen's live evaluation state.

## Setup

### Prerequisites
- Python 3.11+
- A [Groq API key](https://console.groq.com) for the chatbot (`GROQ_API_KEY`)

### Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
pip install python-dotenv groq langchain-groq sentence-transformers
```

> Note: `requirements.txt` covers the core app; `rag/assistant.py` additionally needs `python-dotenv`, `groq`, and `langchain-groq`, and `rag/vector_store.py`'s `HuggingFaceEmbeddings` needs `sentence-transformers`.

### Configure environment

Copy `.env.example` to `.env` and set your key:

```
GROQ_API_KEY=your_key_here
```

### Run

```bash
streamlit run app.py
```

## Data

Schemes live in [`data/schemes_data.json`](data/schemes_data.json). Each entry defines:

- `id`, `name`, `category`, `benefit_type`, `annual_benefit_inr`, `description`
- `eligibility` — criteria such as `min_age`, `max_age`, `max_annual_income`, `occupations`, `owns_land`, `taxpayer`, `enrolled_in_epfo_esic`, `owns_pucca_house`
- `conflicts_with` — IDs of mutually exclusive schemes
- `required_docs` — documents needed to apply

Add or edit schemes by editing this file; no code changes required.

## Screenshots

See `screenshots/screenshot-1.png` and `screenshots/screenshot-2.png`.
