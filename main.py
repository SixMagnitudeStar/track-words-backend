
from fastapi import FastAPI
from database import engine, Base, SessionLocal
from models.models import User
from routers import login , register , logout , profile, chains, words, article, VocabularyList
from security import hash_password
from config import setup_cors
app = FastAPI()
setup_cors(app)

import os
from dotenv import load_dotenv

load_dotenv()

print("SECRET_KEY loaded:", os.getenv("SECRET_KEY"))


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

###############

print("SECRET_KEY loaded:", os.getenv("SECRET_KEY"))


# 建立資料表
Base.metadata.create_all(bind=engine)

# # 預設帳號 admin/password（只在啟動時建立一次）
# def init_user():
#     db = SessionLocal()
#     if not db.query(User).filter_by(username="admin").first():
#         db.add(user.User(username="admin", password="password"))
#         db.commit()
#     db.close()

def init_user():
    db = SessionLocal()
    admin = db.query(User).filter_by(username="admin").first()
    if not admin:
        db.add(User(username="admin", password=hash_password("password")))
    else:
        # 強制更新 admin 密碼為哈希
        admin.password = hash_password("password")
    db.commit()
    db.close()



# def init_user():
#     db = SessionLocal()
#     if not db.query(User).filter_by(username="admin").first():
#         hashed_pwd = hash_password("password")
#         db.add(user.User(username="admin", password=hashed_pwd))
#         db.commit()
#     db.close()

init_user()

# 掛載路由
app.include_router(login.router)
app.include_router(register.router)
app.include_router(logout.router)
app.include_router(profile.router)
app.include_router(chains.router)
app.include_router(words.router)
app.include_router(article.router)

