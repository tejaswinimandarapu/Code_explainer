# Import necessary modules
import os  
import difflib
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate       
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variable
load_dotenv()

# Set the maximum number of lines per chunk
MAX_LINES_PER_CHUNK = 80

# Splits large code blocks into manageable chunks to avoid token overflow
def chunk_code(code, max_lines=MAX_LINES_PER_CHUNK):
    lines = code.splitlines()
    return ["\n".join(lines[i:i + max_lines]) for i in range(0, len(lines), max_lines)]

# Cleans LLM output by removing unnecessary formatting like "markdown" or "text"
def clean_markdown(text):
    if not isinstance(text, str):
        return str(text)
    return text.strip().replace("markdown", "").replace("text", "")

# Check semantic similarity between two texts to avoid repeated explanations.
def is_similar(text1: str, text2: str, threshold: float = 0.97) -> bool:
    return difflib.SequenceMatcher(None, text1, text2).ratio() >= threshold

# Determines if two texts start with the same section heading 
def starts_with_same_section(text1: str, text2: str) -> bool:
    """Check if both texts start with the same structured section title."""
    head1 = text1.strip().split('\n')[0:2]
    head2 = text2.strip().split('\n')[0:2]
    return any(h1 == h2 for h1, h2 in zip(head1, head2))

# Build the LCEL explanation chain with structured prompt logic
def build_explanation_chain():
    prompt = PromptTemplate(
    input_variables=["code", "code_language", "level_of_detail", "output_language"],
    template="""
    You are a multilingual code explanation assistant — an award-winning code reviewer and educator known for explaining complex code in clear, accessible terms.

    Your task:
    1. Explain a programming code snippet written in {code_language}.If the language seems incorrect, explain based on the actual syntax.
    2. Provide the explanation in the user's selected language: {output_language}.
    3. The explanation should be written at a {level_of_detail} level and make a difference between {level_of_detail} (e.g., beginner, intermediate, expert).
    4. Do not include or repeat the original code in your explanation.
    5. Focus on making the explanation beginner-friendly, easy to understand, and technically correct.
    
    Tailor your explanation based on the {level_of_detail} value:
   - If 'Brief': summarize the overall intent in 2–3 sentences with minimal detail.
   - If 'Moderate': explain the main logic and structure without going too deep into every line.
   - If 'Detailed': walk through important code components and logic step-by-step.
   - If 'Comprehensive': provide an in-depth, line-by-line breakdown with reasoning, patterns, and edge cases.

    Structure your explanation using the following format:
    1. Overview – What the code achieves overall.
    2. key Concepts – Important logic, functions, or structures used.
    3. Core Logic – What happens in the code and why.
    4. Edge Cases or Pitfalls – Possible improvements, errors, or limitations.
    5. How It All Connects – How the parts work together to solve the problem.

    Here is the code:

    ```
    {code}
    ```   
        """
    )
    
    # Initialize Google Gemini 2.0 Flash model with API key
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", 
                                 api_key=os.getenv("GOOGLE_API_KEY"), 
                                 temperature=0.7)

    # Return a pipeline where the prompt is passed directly to the LLM
    return prompt | llm

# Explains the provided code based on level of detail and selected language
def explain_code(code: str, code_language="Python", level_of_detail="Detailed", output_language="English"):
    try:
        chain = build_explanation_chain()
        chunks = chunk_code(code)
        explanations = []
        
        # Loop through code chunks and generate explanation for each
        for i, chunk in enumerate(chunks):
            output = chain.invoke({
                "code": chunk,
                "code_language": code_language,
                "level_of_detail": level_of_detail,
                "output_language": output_language
            })

            # Extract and clean the model output
            explanation_text = getattr(output, "content", str(output))
            cleaned = clean_markdown(explanation_text).strip()

            # Avoid adding duplicate or highly similar explanations
            if all(
                not is_similar(cleaned, existing) and not starts_with_same_section(cleaned, existing)
                for existing in explanations
            ):
                explanations.append(cleaned)

        return "\n\n---\n\n".join(explanations) if explanations else "No explanation generated."

    except Exception as e:
        return f"❌ Error: {str(e)}"
 
# Handle user follow-up queries   
def handle_user_query(code, user_query, output_language="English"): 
    prompt = PromptTemplate(
        input_variables=["code", "user_query", "output_language"],
        template="""
        You are a multilingual code explanation assistant, an expert code reviewer and technical educator.

        The user has a question about the following code:

        ```python
        {code}
        ```

        The user asks:
        ```
        {user_query}
        ```

        Please respond in {output_language} using clear, beginner-friendly language.
        Use bullet points or examples where helpful.
        """
    )

    # Initialize a Gemini LLM instance
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )
    
    # Create and invoke the LangChain pipeline for answering user questions
    chain = prompt | llm
    response = chain.invoke({
        "code": code,
        "user_query": user_query,
        "output_language": output_language
    })
    return getattr(response, "content", str(response)).strip()