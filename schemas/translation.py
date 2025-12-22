from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WordToTranslate(BaseModel):
    id: int
    word: str

class BatchUpdateTranslateRequest(BaseModel):
    words: List[WordToTranslate]

class MarkedWordResponse(BaseModel):
    id: int
    user_id: int
    article_id: Optional[int]
    word: str
    translation: Optional[str]
    marked_time: datetime

    class Config:
        orm_mode = True