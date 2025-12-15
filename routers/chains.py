from fastapi import APIRouter, Query
from chains.article_chain import generate_essay  # 新版函式

router = APIRouter()

# @router.get("/essay")
# async def essay_endpoint(
#     topic: str = Query(..., description="Essay topic"),
#     word_limit: int = Query(500, ge=100, le=1000, description="Max words in essay")
# ):
#     # 呼叫新版函式
#     essay = await generate_essay(topic=topic, word_limit=word_limit)
#     return {
#         "topic": topic,
#         "essay": essay.strip()
#     }

@router.get("/essay")
async def essay_endpoint(
    topic: str = Query(..., description="Essay topic"),
    word_limit: int = Query(500, ge=100, le=1000, description="Max words in essay")
):
    # 1. 呼叫新版函式，這時回傳的是字典，例如 {"topic": "...", "content": "..."}
    essay_data = await generate_essay(topic=topic, word_limit=word_limit)
    
    # 2. 直接回傳字典，FastAPI 會自動幫你轉成 JSON
    return {
        "status": "success",
        "topic": essay_data.get("topic", topic),
        "essay": essay_data.get("content", "").strip() # 從字典取出文章內容
    }