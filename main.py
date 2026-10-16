import streamlit as st
import hashlib

from tools import (
    extract_policy_text,
    ask_policy_question,
    generate_policy_summary
)

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="PolicyLens AI",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------------
# APPLICATION TITLE
# -----------------------------------

st.title("🛡️ PolicyLens AI")

st.subheader(
    "Understand Your Insurance Policy with AI"
)

st.write(
    "Upload your insurance policy and get "
    "simple explanations powered by local open-weight models via Ollama."
)

st.info(
    "AI explanations are informational. "
    "Always verify important details with "
    "your insurance provider."
)

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "policy_text" not in st.session_state:
    st.session_state.policy_text = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_id" not in st.session_state:
    st.session_state.file_id = None

# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:
    st.header("Upload Insurance Policy")

    uploaded_file = st.file_uploader(
        "Choose your document",
        type=["pdf", "txt"]
    )

    st.divider()

    st.write("Supported Features")
    st.write("✔ Policy Summarization")
    st.write("✔ Coverage Explanation")
    st.write("✔ Exclusion Detection")
    st.write("✔ Waiting Period Analysis")
    st.write("✔ Claim Condition Explanation")
    st.write("✔ AI Question Answering")

# -----------------------------------
# DOCUMENT PROCESSING
# -----------------------------------

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()

    current_file_id = hashlib.sha256(
        file_bytes
    ).hexdigest()

    if current_file_id != st.session_state.file_id:
        try:
            with st.spinner("Reading your policy..."):
                policy_text = extract_policy_text(
                    uploaded_file
                )

            st.session_state.policy_text = policy_text
            st.session_state.file_id = current_file_id
            st.session_state.messages = []

        except Exception as e:
            st.error(f"Unable to read document: {e}")
            st.stop()

    if not st.session_state.policy_text.strip():
        st.warning(
            "No readable text found. "
            "Scanned PDFs may require OCR."
        )
        st.stop()

    st.success("Policy uploaded successfully!")

    # -----------------------------------
    # APPLICATION TABS
    # -----------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "Policy Summary",
            "Ask AI",
            "Original Document Text"
        ]
    )

    # -----------------------------------
    # POLICY SUMMARY
    # -----------------------------------

    with tab1:
        st.header("Insurance Policy Analysis")

        if st.button("Analyze My Policy"):
            with st.spinner(
                "Ollama is analyzing your policy..."
            ):
                try:
                    summary = generate_policy_summary(
                        st.session_state.policy_text
                    )
                    st.markdown(summary)
                except Exception as e:
                    st.error(str(e))

    # -----------------------------------
    # AI CHAT
    # -----------------------------------

    with tab2:
        st.header("Ask Questions About Your Policy")

        st.write("Example questions:")
        st.write("- What does this insurance cover?")
        st.write("- What are the exclusions?")
        st.write("- What is the waiting period?")
        st.write("- What are the claim conditions?")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input(
            "Ask your insurance question..."
        )

        if question:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = ask_policy_question(
                            st.session_state.policy_text,
                            question
                        )
                    except Exception as e:
                        answer = f"Error: {e}"

                st.markdown(answer)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

    # -----------------------------------
    # ORIGINAL POLICY TEXT
    # -----------------------------------

    with tab3:
        st.header("Extracted Policy Content")

        st.text_area(
            "Document Text",
            st.session_state.policy_text,
            height=450
        )

else:
    st.info(
        "Please upload an insurance policy "
        "to start using PolicyLens AI."
    )
    