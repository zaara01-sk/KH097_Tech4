import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List

def render_top_metrics(results: Dict[str, Any]):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Individually Eligible", f"{len(results['eligible'])} Schemes")
    m2.metric("Mutual Conflicts Detected", f"{len(results['conflicts'])} Conflicts")
    m3.metric("Optimized Bundle Size", f"{len(results['selected_bundle'])} Schemes")
    m4.metric("Max Total Benefit Value", f"₹{results['total_benefit']:,}/yr")
    st.markdown("---")

def render_tab_bundle(selected_bundle: List[Dict[str, Any]]):
    st.subheader("Optimal Non-Conflicting Scheme Bundle")
    st.write("MaxLabh selects schemes that can be combined concurrently while maximizing utility.")

    if not selected_bundle:
        st.warning("No eligible schemes found for this profile. Try adjusting income or attributes in the sidebar.")
        return

    for idx, scheme in enumerate(selected_bundle, 1):
        with st.expander(f"**{idx}. {scheme['name']}** — (Value: ₹{scheme['annual_benefit_inr']:,})", expanded=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**Description:** {scheme['description']}")
                st.write(f"**Category:** `{scheme['category']}` | **Benefit Type:** `{scheme['benefit_type']}`")
            with c2:
                st.metric("Estimated Benefit", f"₹{scheme['annual_benefit_inr']:,}")

    benefit_data = pd.DataFrame([
        {"Scheme": s["name"], "Benefit (INR)": s["annual_benefit_inr"], "Category": s["category"]}
        for s in selected_bundle
    ])
    fig = px.bar(
        benefit_data,
        x="Scheme",
        y="Benefit (INR)",
        color="Category",
        text="Benefit (INR)",
        title="Optimized Bundle Benefit Breakdown (₹/Year)",
        template="plotly_dark"
    )
    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def render_tab_conflicts(conflicts: List[Dict[str, str]], excluded_by_conflict: List[Dict[str, Any]]):
    st.subheader("Mutual Exclusions & Resolution Logic")
    st.write("Examines cross-scheme exclusivity by statute or policy guidelines.")

    if not conflicts:
        st.success("✔ No conflicting schemes found among eligible matches.")
    else:
        st.warning(f"⚠️ {len(conflicts)} cross-scheme conflict(s) detected. The optimizer resolved these.")
        for c in conflicts:
            st.error(f"**Conflict Identified:** `{c['scheme_a']}` is mutually exclusive with `{c['scheme_b']}`.")
            st.markdown(f"> *Reason:* {c['reason']}")

        if excluded_by_conflict:
            st.markdown("### Schemes De-selected by Optimizer")
            for exc in excluded_by_conflict:
                st.info(f"**Excluded:** {exc['name']} (Benefit: ₹{exc['annual_benefit_inr']:,}) — Replaced by higher utility option.")

def render_tab_documents(doc_metrics: Dict[str, Any]):
    st.subheader("Application Readiness Checklist")
    readiness = doc_metrics["readiness_pct"]
    st.progress(readiness / 100.0)
    st.markdown(f"**Current Readiness Score:** `{readiness}%` of required documentation is available.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.success("#### ✅ Verified / In Hand")
        if doc_metrics["available"]:
            for d in doc_metrics["available"]:
                st.write(f"- {d}")
        else:
            st.write("None of the required documents are currently marked.")

    with col_b:
        st.error("#### ❌ Action Required: Missing Documents")
        if doc_metrics["missing"]:
            for d in doc_metrics["missing"]:
                st.write(f"- **{d}** (Procure before applying)")
        else:
            st.write("Great news! The applicant holds all mandatory documents.")

    st.markdown("---")
    st.subheader("Document Mapping by Scheme")
    for scheme_name, docs in doc_metrics["scheme_doc_map"].items():
        st.markdown(f"**{scheme_name}:**")
        st.write(", ".join([f"`{doc}`" for doc in docs]))

def render_tab_audit(eligible: List[Dict[str, Any]], ineligible: List[Dict[str, Any]]):
    st.subheader("Deterministic Eligibility Decision Audit")
    eligible_df = pd.DataFrame([
        {
            "Scheme Name": s["name"],
            "Category": s["category"],
            "Annual Benefit": f"₹{s['annual_benefit_inr']:,}",
            "Status": "Eligible"
        }
        for s in eligible
    ])
    if not eligible_df.empty:
        st.markdown("#### ✅ Criteria Met")
        st.dataframe(eligible_df, use_container_width=True)

    if ineligible:
        st.markdown("#### 🚫 Ineligible Schemes & Rule Disqualifiers")
        ineligible_rows = [
            {
                "Scheme Name": item["scheme"]["name"],
                "Category": item["scheme"]["category"],
                "Disqualification Reasons": " | ".join(item["reasons"])
            }
            for item in ineligible
        ]
        st.dataframe(pd.DataFrame(ineligible_rows), use_container_width=True)