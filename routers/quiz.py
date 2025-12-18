import random
import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from security import get_current_user
from models.models import MarkedWord
from models.models import User
from schemas.quiz import QuizQuestion
from chains.quiz_chain import generate_batch_quiz_options, generate_random_quiz_question

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"],
    responses={404: {"description": "Not found"}},
)

@router.get("/random", response_model=List[QuizQuestion])
async def get_random_quiz(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    count: int = 10
):
    """
    Generates a random quiz with a specified number of questions (default 10).
    It uses the user's marked words first (via a single batch API call), 
    and if there are not enough, it supplements with randomly generated questions.
    """
    quiz_questions: List[QuizQuestion] = []

    # 1. Generate questions from the user's own marked words using batch processing
    user_words_query = db.query(MarkedWord.id, MarkedWord.word).filter(MarkedWord.user_id == current_user.id).distinct()
    user_words = user_words_query.all()
    
    if user_words:
        num_user_questions = min(count, len(user_words))
        selected_words = random.sample(user_words, num_user_questions)
        
        # Create a word-to-id map for easy lookup after batch processing
        word_to_id_map = {word.word: word.id for word in selected_words}
        word_list = list(word_to_id_map.keys())

        # Make a single batch request to the LLM
        llm_results = await generate_batch_quiz_options(word_list)

        for llm_result in llm_results:
            word = llm_result.get("word")
            if word in word_to_id_map:
                correct_answer = llm_result["correct_translation"]
                options = llm_result["distractors"] + [correct_answer]
                random.shuffle(options)
                question = QuizQuestion(
                    id=word_to_id_map[word],
                    word=word,
                    options=options,
                    correct_answer=correct_answer
                )
                quiz_questions.append(question)

    # 2. If not enough questions, supplement with randomly generated ones
    num_to_add = count - len(quiz_questions)
    if num_to_add > 0:
        random_tasks = [generate_random_quiz_question() for _ in range(num_to_add)]
        random_llm_results = await asyncio.gather(*random_tasks)

        for i, llm_result in enumerate(random_llm_results):
            if llm_result:
                correct_answer = llm_result["correct_translation"]
                options = llm_result["distractors"] + [correct_answer]
                random.shuffle(options)
                question = QuizQuestion(
                    id=-(i + 1),  # Use a temporary negative ID
                    word=llm_result["word"],
                    options=options,
                    correct_answer=correct_answer
                )
                quiz_questions.append(question)

    # 3. Final checks and shuffle
    if not quiz_questions:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate any quiz questions. Please try again later."
        )
    
    random.shuffle(quiz_questions)

    return quiz_questions
