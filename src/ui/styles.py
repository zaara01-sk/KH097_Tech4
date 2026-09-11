import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <style>
        .metric-card {
            background-color: #1E293B;
            border-radius: 10px;
            padding: 16px;
            color: white;
            border-left: 5px solid #3B82F6;
        }
        .stAlert {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)