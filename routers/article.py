from fastapi import FastAPI, Header, HTTPException, APIRouter, Depends
from typing import List, Optional
import jwt  # pip install pyjwt


from schemas.schema import AddArticleRequest, AddMarkedWordRequest, AddArticleBlocksRequest ,ArticleRes,AddArticleWithBlocksRequest, MarkedUpdate, MarkedWordRes, UpdateArticleNoteReq, ArticleBlockRes

from security import get_current_user
from database import get_db
from models.models import Article, User, MarkedWord, ArticleBlock

# 匯入 SQLAlchemy 的 Session 類型，用於與資料庫互動
from sqlalchemy.orm import Session
import json

# 引入排序資料desc
from sqlalchemy import desc

from fastapi import Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

# 建立一個 APIRouter 實例，讓這個檔案可以獨立作為路由模組
router = APIRouter()


## 測試用，之後要拿掉
@router.get("/testarticle", response_model=List[ArticleRes])
def findarticle(db: Session = Depends(get_db)):
    articles = db.query(Article)\
    .options(joinedload(Article.blocks))\
    .order_by(desc(Article.id))\
    .all()
    
    # if articles:
    #     return {'文章': articles}
    # else:
    #     return {'回答': '找不到'}
    #return articles
    return articles





from fastapi.encoders import jsonable_encoder

# @router.get('/articles', response_model=List[ArticleRes])
# def get_articles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     articles = db.query(Article)\
#         .filter(Article.user_id == current_user.id)\
#         .options(
#             joinedload(Article.blocks),
#             joinedload(Article.marked_words)
#         )\
#         .order_by(desc(Article.id))\
#         .all()

#     result = []
#     for article in articles:
#         blocks = [
#             ArticleBlockRes(
#                 id=b.id,
#                 text=b.text,
#                 text_type=b.text_type,
#                 marked=b.marked,
#                 index=b.index,
#                 style=b.style,
#                 previous_index=b.previous_index,
#                 next_index=b.next_index
#             )
#             for b in article.blocks
#         ]

#         marked_words = [
#             MarkedWordRes(
#                 id=mw.id,
#                 article_id=mw.article_id,
#                 word=mw.word
#             )
#             for mw in article.marked_words
#         ]

#         article_data = ArticleRes(
#             id=article.id,
#             title=article.title,
#             note=article.note,
#             content=article.content,
#             blocks=blocks,
#             marked_words=marked_words
#         )

#         result.append(article_data)

#     return result

## 文章查詢 (包含所有block、marked word)
@router.get('/articles', response_model=List[ArticleRes])
def get_articles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    articles = db.query(Article)\
        .filter(Article.user_id == current_user.id)\
        .options(
            joinedload(Article.blocks),
            joinedload(Article.marked_words)
        )\
        .order_by(desc(Article.id))\
        .all()

    result = []
    for article in articles:
        blocks = [
            ArticleBlockRes(
                id=b.id,
                text=b.text,
                text_type=b.text_type,
                marked=b.marked,
                index=b.index,
                style=b.style,
                previous_index=b.previous_index,
                next_index=b.next_index
            )
            for b in article.blocks
        ]

        marked_words = [
            MarkedWordRes(
                id=mw.id,
                article_id=mw.article_id,
                word=mw.word
            )
            for mw in article.marked_words
        ]

        article_data = ArticleRes(
            id=article.id,
            title=article.title,
            note=article.note,
            content=article.content,
            blocks=blocks,
            marked_words=marked_words
        )

        result.append(article_data)

    return result
# @router.get('/articles', response_model=List[ArticleRes])
# def get_articles(current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
#     articles = db.query(Article)\
#     .filter(Article.user_id == current_user.id)\
#     .options(joinedload(Article.blocks))\
#     .order_by(desc(Article.id))\
#     .all()
#     ##return {'message': '文章查詢成功', 'account': current_user.username, 'articles': articles}

#     result = []
#     for article in articles:
#         # 查該文章的 marked_words
#         words = [
#             MarkedWordRes(
#                 id=mw.id,
#                 article_id=mw.article_id,
#                 word=mw.word
#             )
#             for mw in db.query(MarkedWord).filter(MarkedWord.article_id == article.id).all()
#         ]

#         article_data = ArticleRes.from_orm(article).model_copy(update={"marked_words": words})

#         result.append(article_data.dict())
#     return result

# @router.get('/articles')
# def get_articles(current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
#     articles = db.query(Article).filter(Article.user_id == current_user.id).order_by(desc(Article.id)).all()

#     # 將 Article 物件 list 轉成 dict list
#  ##   articles_list = [article_to_dict(a) for a in articles]

#     return {'message': '文章查詢成功', 'account': current_user.username, 'articles': articles}



def article_to_dict(article: Article):
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        # "tags_css": json.loads(article.tags_css) if article.tags_css else []
        "tags_css": article.tags_css or []
    }


@router.post('/article')
def add_article(req: AddArticleWithBlocksRequest,current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return {"message": "請先登入"}

    new_article = Article(user_id = current_user.id,title=req.title, content = req.content, note=req.note)
    db.add(new_article)
    db.commit()
    db.refresh(new_article) ## 沒有要回傳值，其實可以不用refresh

    print('提交文章成功');

    for i in req.blocks:
        new_block = ArticleBlock(
            user_id = current_user.id,
            article_id = new_article.id,
            index = i.index,
            text = i.text,
            text_type = i.text_type,
            style = i.style,
            previous_index = i.previous_index,
            next_index = i.next_index
        )
        db.add(new_block)

    db.commit()  # 一次性提交所有 block

    print('提交block成功')

    return {
        'message': '文章新增成功!',
        'account': current_user.username,
        'article': {
            'id': new_article.id,
            'title': req.title,
            'content': req.content,
            'blocks_count': len(req.blocks)
        }
    }



@router.put('/article/{article_id}')
def update_article(
    article_id: int,
    req: AddArticleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")

    # 找文章
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.user_id == current_user.id   # 確保只能改自己的文章
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 更新內容
    article.title = req.title
    article.content = req.content
    article.tags_css = req.tags_css
    article.note = req.note

    db.commit()
    db.refresh(article)

    return {
        "message": "文章修改成功!",
        "article": article_to_dict(article)
    }

@router.delete('/article/{article_id}')
def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")

    # 找文章
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.user_id == current_user.id   # 確保只能改自己的文章
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(article)
    db.commit()

    return {
        "message": "文章刪除成功!",
        "account": current_user.username,
        "deleted_article": article
    }



@router.get('/article_blocks')
def get_article_blocks(current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    article_blocks = db.query(ArticleBlock).filter(
        ArticleBlock.user_id == current_user.id, ArticleBlock.article_id
        ).order_by(desc(ArticleBlock.index)).all()

    # 將 Article 物件 list 轉成 dict list
    articles_list = [article_to_dict(a) for a in articles]

    return {'message': '文章查詢成功', 'account': current_user.username, 'articles': articles}


@router.post('/article_blocks/batch')
def add_article_blocks(
    request: AddArticleBlocksRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 將每筆 block 加上 user_id
    block_dicts = []
    for b in request.blocks:
        d = b.dict()
        d['user_id'] = current_user.id
        block_dicts.append(d)

    # 使用 bulk_insert_mappings 批量新增
    db.bulk_insert_mappings(ArticleBlock, block_dicts)
    db.commit()

    return {
        'message': '文章區塊批量新增成功',
        'account': current_user.username,
        'added_count': len(block_dicts)
    }



# @router.get('/markedwords/{article_id}')
# def get_markwords(
#     article_id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):

#     markedwords = db.query(
#         MarkedWord).filter(MarkedWord.user_id == current_user.id, 
#         MarkedWord.article_id == article_id
#         ).all()

#     return {'message': '標記單字查詢成功!', 'words': markedwords}    

@router.get('/markedwords')
def get_markwords(
    article_id: int | None = Query(None),
    marked_from: datetime | None = Query(None),
    marked_to: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1) 建立一個 query 物件（還沒執行）
    q = db.query(MarkedWord).filter(MarkedWord.user_id == current_user.id)

    # 2) 根據有沒有傳參數，動態加上 filter（仍然沒執行）
    if article_id is not None:
        q = q.filter(MarkedWord.article_id == article_id)

    if marked_from is not None:
        q = q.filter(MarkedWord.marked_time >= marked_from)

    if marked_to is not None:
        q = q.filter(MarkedWord.marked_time <= marked_to)

    # 排序、分頁等也可以在這裡加入
    q = q.order_by(MarkedWord.marked_time.desc())

    if limit is not None:
        q = q.limit(limit)

    # 3) 最後執行（在這一行 SQL 才會被送到 DB）
    results = q.all()

    return {"message": "標記單字查詢成功!", "words": results}


@router.post('/markedword')
def upldate_markedword(
    req: AddMarkedWordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")
    
    new_item = MarkedWord(user_id=current_user.id, article_id=req.article_id, word=req.word)
    db.add(new_item)
    db.commit()

    return {'message':'標記單字新增成功!','account':current_user.username, 'word':req.word}




## 只刪除查詢到的第一筆
@router.delete('/markedword')
def delete_markedword(
    article_id: Optional[int] = Query(None),
    word: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="請先登入")

    if not any([article_id, word]):
        raise HTTPException(status_code=400, detail="請提供至少一個刪除條件")

    query = db.query(MarkedWord).filter(MarkedWord.user_id == current_user.id)

    if article_id is not None:
        query = query.filter(MarkedWord.article_id == article_id)
    if word is not None:
        query = query.filter(MarkedWord.word == word)

    item = query.first()  # 只取第一筆

    if not item:
        raise HTTPException(status_code=404, detail="找不到符合條件的標記單字")

    db.delete(item)
    db.commit()

    return {
        "message": "成功刪除標記單字!",
        "account": current_user.username,
        "deleted_word": item.word
    }



@router.patch("/article-blocks/{block_id}/marked")
def update_block_marked(block_id: int, data: MarkedUpdate, db: Session = Depends(get_db)):
    block = db.query(ArticleBlock).filter(ArticleBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    block.marked = data.marked
    db.commit()
    db.refresh(block)

    return {
        "message": "Marked status updated",
        "block_id": block_id,
        "marked": block.marked
    }




@router.patch("/article/note")
def update_article_note(
    req: UpdateArticleNoteReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ 先找到那篇文章（條件用 == 要在欄位上）
    article = (
        db.query(Article)
        .filter(Article.id == req.article_id, Article.user_id == current_user.id)
        .first()
    )

    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned by user")

    # 2️⃣ 更新 note 欄位
    article.note = req.note

    # 3️⃣ 寫回資料庫
    db.commit()
    db.refresh(article)

    # 4️⃣ 回傳更新結果
    return {
        "message": "Note updated!",
        "article_id": article.id,
        "note": article.note,
    }

# @router.delete('/markedword/{id}')
# def delete_markedword(
#     id: int,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     if not current_user:
#         raise HTTPException(status_code=401, detail="請先登入")

#     # 找出要刪除的紀錄
#     item = db.query(MarkedWord).filter_by(
#         id=id,
#         user_id=current_user.id
#     ).first()

#     if not item:
#         raise HTTPException(status_code=404, detail="找不到對應的標記單字")

#     db.delete(item)
#     db.commit()

#     return {
#         "message": "標記單字刪除成功!",
#         "account": current_user.username,
#         "word": item.word
#     }