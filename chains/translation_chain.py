import os
from dotenv import load_dotenv
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load environment variables from .env file
load_dotenv()

# Get the API Key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not set in environment variables")

# 1. Initialize the language model with JSON mode
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=api_key,
    response_mime_type="application/json"
)

# 2. Define the JSON output parser
parser = JsonOutputParser()

# 3. Create the prompt template
# This prompt instructs the model to translate a list of words into Traditional Chinese
# and return the result as a JSON object.
template = """
You are a helpful translation assistant. Your task is to translate a list of English words into Traditional Chinese (繁體中文).
Provide the output strictly as a single JSON object where the keys are the original English words and the values are their Chinese translations.

Here is the list of words to translate:
{words}

JSON Output:
"""
prompt = PromptTemplate.from_template(template)

# 4. Define the translation chain
chain = prompt | llm | parser

async def batch_translate_words(words: List[str]) -> Dict[str, str]:
    """
    Asynchronously translates a batch of words using the Gemini LLM.
    
    Args:
        words: A list of English words to translate.
        
    Returns:
        A dictionary mapping each original word to its translation.
    """
    # The input to the chain is a dictionary
    inputs = {"words": words}
    
    # Invoke the chain asynchronously
    try:
        translation_dict = await chain.ainvoke(inputs)
        return translation_dict
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        # Return an empty dictionary or handle the error as needed
        return {}

