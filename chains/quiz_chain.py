import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load environment variables from .env file
load_dotenv()

# Get API Key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not set in environment variables")

# 1. Initialize the model (with JSON Mode)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=api_key,
    response_mime_type="application/json"
)

# --- Pydantic Models for Parsing ---
class QuizDataItem(BaseModel):
    word: str = Field(description="The original English word.")
    correct_translation: str = Field(description="The correct Chinese translation.")
    distractors: List[str] = Field(description="A list of three plausible but incorrect Chinese translations.")

class QuizDataList(BaseModel):
    quiz_data: List[QuizDataItem] = Field(description="A list of quiz data objects.")

# --- Single Word Generation (for random fill-ins) ---
prompt_for_random = PromptTemplate.from_template("""
You are an English-Chinese translation quiz assistant. 
Your task is to generate a complete quiz question by:
1. Picking a common English word suitable for a language learner (e.g., from CEFR A2-B2 levels).
2. Providing the most common Chinese translation for that word.
3. Providing three plausible but incorrect Chinese words to serve as distractors.

IMPORTANT: All Chinese output, including translations and distractors, MUST be in Traditional Chinese (繁體中文).

Please provide your response strictly in JSON format with three keys: "word", "correct_translation", and "distractors".
Example response: {{"word": "computer", "correct_translation": "電腦", "distractors": ["電視", "電話", "計算機"]}}
""")
parser_for_random = JsonOutputParser(pydantic_object=QuizDataItem)
chain_for_random = prompt_for_random | llm | parser_for_random

async def generate_random_quiz_question() -> dict:
    try:
        return await chain_for_random.ainvoke({})
    except Exception as e:
        print(f"Error generating random quiz question: {e}")
        return None

# --- Batch Word Generation (for user's words) ---
template_for_batch = PromptTemplate.from_template("""
You are an English-Chinese translation quiz assistant. 
For the given list of English words, your task is to return a JSON object for each word containing its most common Chinese translation and three plausible but incorrect Chinese distractors.

IMPORTANT: All Chinese output, including translations and distractors, MUST be in Traditional Chinese (繁體中文).

Process all words in this list: {words}

Provide your response as a single JSON object with a single key "quiz_data", which contains a list of JSON objects.
Each object in the list must have the following keys: "word", "correct_translation", and "distractors".

Example Request:
words: ["apple", "car"]

Example Response:
{{
    "quiz_data": [
        {{
            "word": "apple",
            "correct_translation": "蘋果",
            "distractors": ["香蕉", "梨子", "螢幕"]
        }},
        {{
            "word": "car",
            "correct_translation": "汽車",
            "distractors": ["火車", "飛機", "自行車"]
        }}
    ]
}}
""")
parser_for_batch = JsonOutputParser(pydantic_object=QuizDataList)
chain_for_batch = template_for_batch | llm | parser_for_batch

async def generate_batch_quiz_options(words: List[str]) -> List[dict]:
    """
    Asynchronously generates quiz data for a batch of words in a single API call.
    """
    if not words:
        return []
    
    inputs = {"words": ", ".join(words)}
    try:
        result = await chain_for_batch.ainvoke(inputs)
        return result.get("quiz_data", [])
    except Exception as e:
        print(f"Error generating batch quiz options for words '{words}': {e}")
        return []
