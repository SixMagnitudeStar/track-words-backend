from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.models import VocabularyList, User
from schemas.schema import VocabularyListCreate,  VocabularyListUpdate, VocabularyListWordCreate
from database import get_db
from security import get_current_user

router = APIRouter(prefix="/vocabulary_lists", tags=["vocabulary_lists"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vocabulary_list(req: VocabularyListCreate,
                           current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")

    new_list = VocabularyList(
        user_id=current_user.id,
        name=req.name,
        description=req.description
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    return {
        "message": "列表新增成功",
        "list": {
            "id": new_list.id,
            "name": new_list.name,
            "description": new_list.description
        }
    }


@router.put("/{list_id}")
def update_vocabulary_list(list_id: int,
                           req: VocabularyListUpdate,
                           current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")


    target = db.query(VocabularyList).filter(VocabularyList.id == list_id).first()
    
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="list not found")
    if target.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="非擁有者")

    if req.name is not None:
        target.name = req.name
    if req.description is not None:
        target.description = req.description

    db.commit()
    db.refresh(target)

    return {
        "message": "列表更新成功",
        "list": {
            "id": target.id,
            "name": target.name,
            "description": target.description
        }
    }

@router.delete("/{list_id}", status_code=status.HTTP_200_OK)
def delete_vocabulary_list(list_id: int,
                           current_user: User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")

    target = db.query(VocabularyList).filter(VocabularyList.id == list_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="list not found")
    if target.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="非擁有者")

    db.delete(target)
    db.commit()

    return {"message": "列表刪除成功"}



@router.post("/{list_id}/words", status_code=status.HTTP_201_CREATED)
def add_word_to_vocabulary_list(list_id: int,
                                req: VocabularyListWordCreate,
                                current_user: User = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")

    target = db.query(VocabularyList).filter(VocabularyList.id == list_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="list not found")
    if target.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="非擁有者")

    new_word = VocabularyListWord(
        list_id=list_id,
        word=req.word
    )
    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    return {
        "message": "單字新增成功",
        "word": {
            "id": new_word.id,
            "list_id": new_word.list_id,
            "word": new_word.word
        }
    }

@router.delete("/{list_id}/words/{word_id}", status_code=status.HTTP_200_OK)
def delete_word_in_vocabulary_list(list_id: int,
                                   word_id: int,
                                   current_user: User = Depends(get_current_user),
                                   db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="請先登入")

    target = db.query(VocabularyList).filter(VocabularyList.id == list_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="list not found")

    if target.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="非擁有者")

    target_word = db.query(VocabularyListWord).filter(
        VocabularyListWord.id == word_id,
        VocabularyListWord.list_id == list_id
    ).first()
    
    if not target_word:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="word not found")

    db.delete(target_word)
    db.commit()

    return {"message": "單字刪除成功", "word_id": word_id}