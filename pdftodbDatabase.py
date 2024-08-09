from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # MCQ, YES_NO, IMAGE

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    answer_text = Column(Text, nullable=False)

class ImageQuestion(Base):
    __tablename__ = 'image_questions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)

# Update the connection string for PostgreSQL
DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/onlinetest01'

# Database connection
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
