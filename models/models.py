from sqlalchemy import Column, Integer, String, Boolean ,ForeignKey, JSON, Index, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import expression
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    nickname = Column(String)

    articles = relationship("Article", back_populates="user")


class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    note = Column(String)

    content = Column(String)

    user = relationship("User", back_populates="articles")
    # marked_words = relationship("MarkedWord")
    marked_words = relationship("MarkedWord", back_populates="article")

    # 加上 blocks relationship
    blocks = relationship(
        "ArticleBlock",
        backref="article",
        cascade="all, delete-orphan",
        order_by="ArticleBlock.index"
    )



# class ArticleBlock(Base):
#     __tablename__ = 'article_block'

#     id = Column(Integer, primary_key=True, index = True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     article_id = Column(Integer, ForeignKey('articles.id')) 

#     text = Column(String)
#     text_type = Column(String)

#     marked = Column(Boolean,  default=False,  server_default=expression.false(), nullable=False)

#         # self-reference
#     previous_id = Column(Integer, ForeignKey("article_block.id"), nullable=True)
#     next_id = Column(Integer, ForeignKey("article_block.id"), nullable=True)

#     # relationships
#     previous = relationship(
#         "ArticleBlock",
#         remote_side=[id],
#         foreign_keys=[previous_id],
#         backref="next_block"
#     )

#     next = relationship(
#         "ArticleBlock",
#         remote_side=[id],
#         foreign_keys=[next_id],
#         backref="previous_block"
#     )

class ArticleBlock(Base):
    __tablename__ = 'article_block'

    id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('articles.id')) 

    text = Column(String)
    text_type = Column(String)

    style = Column(String)

    marked = Column(Boolean,  default=False,  server_default=expression.false(), nullable=False)

    index = Column(Integer, nullable=True)
        # self-reference
    previous_index = Column(Integer, nullable=True)
    next_index = Column(Integer, nullable=True)



Index("ix_article_block_article", ArticleBlock.article_id)

class MarkedWord(Base):
    __tablename__ = 'marked_words'
    id = Column(Integer, primary_key=True)   # 流水號
  
    user_id = Column(Integer, ForeignKey('users.id'))

    # 這個 mark的單字屬於哪篇文章
    ## article_id = Column(Integer, ForeignKey('articles.id')) 
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=True)
    word = Column(String)                    # mark 的單字

    marked_time = Column(DateTime, default=datetime.utcnow)


    article = relationship("Article", back_populates="marked_words")


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    word = Column(String)


class testmodel(Base):
    __tablename__ = 'testmodel'

    id = Column(Integer, primary_key=True, index=True)

    m = Column(String)
    a = Column(String)
    c = Column(String)

# class Note(Base):
#     __tablename__ = 'notes'

#     id = Column(Integer, primary_key = True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     article_id = Column(Integer, ForeignKey('articles.id'))

#     text = Column(String)