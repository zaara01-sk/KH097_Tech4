import streamlit as st
from typing import Dict, Any

def render_chatbot_view(chatbot, evaluation_state: Dict[str, Any], citizen_profile: Dict[str, Any]):
    st.subheader("💬 MaxLabh Sahayak — Entitlement AI Advisor")
    st.caption("Ask questions about scheme benefits, application prerequisites, or why certain schemes were bundled or excluded. Answers in your prompt's language.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Namaste! I am your MaxLabh Advisor. Aap mujhse kisi bhi scheme, document, ya eligibility ke baare mein pooch sakte hain."
            }
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("e.g., Kya main PM-KISAN ke liye eligible hu? / Why was APY chosen?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing rules & your profile..."):
                response = chatbot.answer_query(
                    question=prompt,
                    evaluation_state=evaluation_state,
                    citizen_profile=citizen_profile
                )
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})