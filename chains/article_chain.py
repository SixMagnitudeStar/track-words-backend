##from langchain.chat_models import ChatGoogleGemini
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

##from langchain.chains import LLMChain //舊版，改用PromptValue
from langchain_core.prompt_values import PromptValue

# 載入 .env 檔的內容到系統環境變數
load_dotenv()

# 從環境變數讀取 API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not set in environment variables")

# 1. 初始化模型 (開啟 JSON Mode)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",   # 改成目前可用模型
    temperature=0,
    google_api_key=api_key,  # 明確傳入 API Key
    response_mime_type="application/json"
    )

# 2. 定義 JSON 解析器
parser = JsonOutputParser()


# 3. 模板 (建議使用 JSON Schema 描述更精確)
template = """
You are an expert essay writer. I will provide a general theme or topic direction. 
Your task is to:
1. Create a specific, catchy, and professional title based on that theme.
2. Write a high-quality English short essay (no more than {word_limit} words) based on that specific title.

General Theme: {topic}

Output the result strictly as a JSON object with the following structure:
{{
    "topic": "Put the specific, creative title you generated here",
    "content": "Put the full essay content here"
}}
"""
prompt = PromptTemplate.from_template(template)

## 定義管線
chain = prompt | llm | parser

async def generate_essay(topic: str, word_limit: int = 100) -> str:
    """
    非同步生成短文（新版 LangChain）
    """
    # 先把參數包成 dict
    inputs = {"topic": topic, "word_limit": word_limit}

    # 執行管線
    result_dict = await chain.ainvoke(inputs)
    
    print('解析後的結果:', result_dict)
    
    # 因為使用了 JsonOutputParser，result_dict 已經是 {'topic': '...', 'content': '...'}
    return result_dict
    ##return essay_text.strip()


