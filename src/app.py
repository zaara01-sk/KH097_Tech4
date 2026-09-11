import os
import streamlit as st
from core.engine import SchemeEngine
from pipeline import OptimizationPipeline, RAGPipeline
from ui import (
    apply_custom_styles,
    render_sidebar,
    render_top_metrics,
    render_tab_bundle,
    render_tab_conflicts,
    render_tab_documents,
    render_tab_audit,
    render_chatbot_view
)

st.set_page_config(
    page_title="MaxLabh — Autonomous Scheme-Bundle Optimizer",
    page_icon="🏹",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "schemes_data_converted.json")

@st.cache_resource
def get_pipelines():
    engine = SchemeEngine(DATA_PATH)
    opt_pipeline = OptimizationPipeline(engine)
    rag_pipeline = RAGPipeline(DATA_PATH)
    return opt_pipeline, rag_pipeline

optimizer_pipe, rag_pipe = get_pipelines()

citizen_profile = render_sidebar()

st.title("🏹 MaxLabh: Autonomous Scheme-Bundle Optimizer")
st.caption("Deterministic Constraint Optimization & Multilingual RAG Advisory")

results = optimizer_pipe.run(citizen_profile)

render_top_metrics(results)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Recommended Optimal Bundle",
    "⚡ Conflict Resolution Engine",
    "📋 Document Readiness & Action Plan",
    "🔍 Full Eligibility Audit Trail",
    "💬 Ask Sahayak (AI Advisor)"
])

with tab1:
    render_tab_bundle(results["selected_bundle"])

with tab2:
    render_tab_conflicts(results["conflicts"], results["excluded_by_conflict"])

with tab3:
    render_tab_documents(results["doc_metrics"])

with tab4:
    render_tab_audit(results["eligible"], results["ineligible"])

with tab5:
    render_chatbot_view(rag_pipe.assistant, results, citizen_profile)
