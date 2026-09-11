import streamlit as st
from typing import Dict, Any

def render_sidebar() -> Dict[str, Any]:
    st.sidebar.header("👤 Citizen Profile (Input)")

    age = st.sidebar.slider("Applicant Age", min_value=16, max_value=85, value=34, step=1)
    occupation = st.sidebar.selectbox(
        "Primary Occupation",
        ["Unorganized Worker", "Farmer", "Street Vendor", "Daily Wage Earner", "Artisan", "Salaried", "Self-Employed"]
    )
    annual_income = st.sidebar.number_input(
        "Gross Annual Family Income (₹)",
        min_value=20000,
        max_value=2000000,
        value=140000,
        step=10000
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Additional Attributes")
    owns_land = st.sidebar.checkbox("Owns Agricultural Land", value=False)
    taxpayer = st.sidebar.checkbox("Is Income Tax Payer", value=False)
    enrolled_epfo = st.sidebar.checkbox("Active EPFO/ESIC Member", value=False)
    secc_eligible = st.sidebar.checkbox("SECC 2011 / Ration Card Beneficiary", value=True)
    owns_pucca_house = st.sidebar.checkbox("Owns a Pucca House", value=False)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Documents Currently Available")
    doc_options = [
        "Aadhaar Card",
        "Bank Passbook",
        "Land Ownership Proof (ROR)",
        "Savings Bank Account / Jan Dhan Account",
        "Bank Account",
        "Vending Certificate / Urban Local Body ID Card",
        "Ration Card",
        "SECC Inclusion Certificate",
        "PAN Card",
        "Business Address Proof",
        "MGNREGA Job Card",
        "Certificate of Kutcha House"
    ]
    held_documents = st.sidebar.multiselect(
        "Select citizen's existing documents:",
        doc_options,
        default=["Aadhaar Card", "Bank Passbook", "Ration Card", "Savings Bank Account / Jan Dhan Account"]
    )

    return {
        "age": age,
        "occupation": occupation,
        "annual_income": annual_income,
        "owns_land": owns_land,
        "taxpayer": taxpayer,
        "enrolled_in_epfo_esic": enrolled_epfo,
        "secc_eligible": secc_eligible,
        "owns_pucca_house": owns_pucca_house,
        "documents": held_documents
    }