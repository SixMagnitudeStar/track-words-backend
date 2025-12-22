from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from schemas.translation import BatchUpdateTranslateRequest, MarkedWordResponse, WordToTranslate
from chains.translation_chain import batch_translate_words
from security import get_current_user
from models.models import User, MarkedWord
from database import get_db

# Create an APIRouter instance for the translation endpoints
router = APIRouter()

@router.post('/translate/batch-update', response_model=List[MarkedWordResponse])
async def handle_batch_update_translate(
    request: BatchUpdateTranslateRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    API endpoint to:
    1. Translate a batch of words.
    2. Update the 'translation' field for each word in the database.
    3. Return the updated MarkedWord objects.
    """
    if not request.words:
        return []

    # 1. Extract words to be translated
    words_to_translate = [item.word for item in request.words]
    
    # 2. Call the translation chain function
    translations_map = await batch_translate_words(words_to_translate)
    
    if not translations_map:
        raise HTTPException(
            status_code=500, 
            detail="Failed to get translations from the service."
        )

    # 3. Update database records
    updated_ids = []
    for item in request.words:
        word_id = item.id
        original_word = item.word
        
        if original_word in translations_map:
            translation_text = translations_map[original_word]
            
            # Find the MarkedWord by id and user_id to ensure security
            word_to_update = db.query(MarkedWord).filter(
                MarkedWord.id == word_id,
                MarkedWord.user_id == current_user.id
            ).first()

            if word_to_update:
                word_to_update.translation = translation_text
                updated_ids.append(word_id)

    db.commit()

    # 4. Query and return the updated objects
    if not updated_ids:
        return []
        
    updated_words = db.query(MarkedWord).filter(MarkedWord.id.in_(updated_ids)).all()
    
    return updated_words