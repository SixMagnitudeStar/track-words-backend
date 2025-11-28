from pydantic import BaseModel
from typing import List, Optional






class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AddWordRequest(BaseModel):
    word: str


class AddArticleRequest(BaseModel):
    title: str
    content: str
    note: str



class AddArticleBlockRequest(BaseModel):
    index: int
    text: str
    text_type: str
    previous_index: Optional[int] = None
    next_index: Optional[int] = None
    style: Optional[str] = None  # <- 可選
    # previous_index: int
    # next_index: int

class AddArticleBlocksRequest(BaseModel):
    blocks: List[AddArticleBlockRequest]

class AddMarkedWordRequest(BaseModel):
    article_id: int
    word: str



class ArticleBlockRes(BaseModel):
    id: int
    text: str
    text_type: str

    marked: bool
    index: int
    style: Optional[str] = None  # <- 可選

    previous_index: Optional[int] = None
    next_index: Optional[int] = None

    class Config:
        from_attributes = True
    # class Config:
    #     orm_mode = True

class MarkedWordRes(BaseModel):
    id: int
    article_id: int
    word: str


class ArticleRes(BaseModel):
    id: int
    title: str
    content: str
    note: Optional[str] = ''
    blocks: List[ArticleBlockRes] = []
    marked_words: List[MarkedWordRes] = []
    
    class Config:
        from_attributes = True    

    # class Config:
    #     orm_mode = True


class AddArticleWithBlocksRequest(BaseModel):
    title: str
    content: str
    note: str
    blocks: List[AddArticleBlockRequest] = []   # 預設空陣列




class MarkedUpdate(BaseModel):
    marked: bool


class UpdateArticleNoteReq(BaseModel):
    article_id : int
    note : str


##################################

## 詞彙列表創建與修改請求提交表單
class VocabularyListCreate(BaseModel):
    name: str  # 建立必填
    description: Optional[str] = None

class VocabularyListUpdate(BaseModel):
    name: Optional[str] = None  # 注意 Optional 寫法
    description: Optional[str] = None  # 拼寫 correction

## 詞彙料表內的單字創建請求    
class VocabularyListWordCreate(VocabularyListWordBase):
    list_id: int
    word = str

## 回傳給前端的值，有驗證比較乾淨
class VocabularyListWordOut(BaseModel):
    id: int
    list_id: int
    word: str

    class Config:
        orm_mode = True