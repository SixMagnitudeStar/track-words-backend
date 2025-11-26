from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import SessionLocal
from models.models import User
from schemas.schema import LoginRequest, TokenResponse

from database import get_db
from security import verify_password, create_access_token

router = APIRouter()


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    使用者登入：產生 JWT Token
    """
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password.")

    # 產生 JWT token
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users")
def look(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return {'使用者帳號': users}

