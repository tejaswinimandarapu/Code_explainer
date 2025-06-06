# Import necessary modules
import streamlit as st
import os
from code_explainer import *

# Configure the Streamlit page layout
st.set_page_config(
    page_title="Code Explainer",
    page_icon="🤖",
    layout="wide"
)
st.title("🤖 Code Explainer")
st.markdown("""
This application helps you to understand the code snippets by providing detailed explanations.
Enter your code below and get a comprehensive breakdown of how it works!
""")

# Divide the screen into two equal columns for input and output
col1, col2 = st.columns([1, 1])

# Left side: Input code section 
with col1:
    st.subheader("🧾Input Code:")
    code_language = st.selectbox(
        "✨Select the programming language (optional):",
        ["Python", "JavaScript", "Java", "C++", "C#", "Ruby", "Go", "PHP", "Swift", "TypeScript", "Other"]
    )
    
    # Two tabs: one for pasting code, another for uploading a file
    tab1, tab2 = st.tabs(["📝 Paste Code", "📁 Upload File"])
    
    # Tab for pasting code
    with tab1:
        code_input = st.text_area(
        label="",
        placeholder="Paste your code here (e.g., Python, Java, etc.)",
        height=300,
        label_visibility="collapsed"
        )
        
    with tab2:
        uploaded_file = st.file_uploader("Choose a file", type=["py","cs", "txt", "js", "java", "cpp", "rb", "go", "php", "swift", "ts", "code"])
    
    # Read file content and show a preview if a file was uploaded
    if uploaded_file is not None:
        code_input = uploaded_file.read().decode("utf-8")
        st.code(code_input, language=code_language, height=300)
        st.success(f"✅File Loaded: `{uploaded_file.name}`")
    
# Slider to select level of explanation detail  
detail_level = detail_range = detail_level = st.select_slider(
    label="Select explanation depth:",
    options=["Brief", "Moderate", "Detailed", "Comprehensive"],
    value="Detailed"
)

# Button to trigger code explanation
explain_button = st.button("✅Explain code", type="primary")

# SIDEBAR: OUTPUT LANGUAGE + FOLLOW-UP QUESTIONS
with st.sidebar:
    st.markdown("## 🤖 Code Explainer Assistant")
    st.caption("AI-powered multilingual code understanding")
    
    # Dropdown to select language for explanation output
    st.title("Choose Language🌐")
    output_language = st.selectbox(
        "ℹ️ Choose the language in which you want the explanation",
        ['English', 'Hindi', 'Telugu', 'Tamil', 'Malayalam', 'Kannada', 'Bengali', 'Marathi', 'Urdu', 'Others']
    )
    st.markdown("---")

     # Text box for user follow-up questions about the code
    st.subheader("Ask Follow-up Questions:")
    user_query = st.text_area("What would you like to know about the code?", key="follow_up_query", height = 200)
    
    # Container for the follow-up response
    followup_response_container = st.container()
    st.button("Explain")

    # If user asks a question and code is present, generate response
    if user_query and st.button:
        if code_input:
            with st.spinner("Thinking..."):
                response = handle_user_query(code_input, user_query, output_language)
                st.session_state["output_explanation"] = response
            with followup_response_container:
                st.markdown("### 💡 Response:")
                st.write(response)
        elif user_query and not code_input:
            st.error("❌ Please enter or upload code first.")


# RIGHT SIDE: CODE EXPLANATION OUTPUT
with col2:
    st.subheader("📘Code Explanation:")
    explanation_container = st.container(height=444)
    
    # If explain button pressed and code is available, process explanation
    if explain_button and code_input:
        with st.spinner("Explaining your code... please wait ⏳"):
            explanation = explain_code(code_input, code_language, detail_level, output_language)
            st.success("✅ Explanation ready!")
            st.session_state["output_explanation"] = explanation
        with explanation_container:
                st.markdown(explanation)
                
    # Default message shown before code explanation is generated
    elif explain_button and not code_input:
        with explanation_container:
            st.error("Please enter some code to explain.")
    else:
        with explanation_container:
            st.info("💡 Your code explanation will appear here once you run the tool.")          
            
# A button to download the explanation if it exists
if 'explanation' in locals() and explanation.strip():
    st.download_button(
        label="⬇️ Download Explanation",
        data=explanation,
        file_name="code_explanation.md",
        mime="text/markdown"
        )

# Footer
st.markdown("---")
st.caption("🔧 Feel free to get explanation")
st.markdown("")