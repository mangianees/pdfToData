import re
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
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

# Database connection - use your actual PostgreSQL database URL
DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/onlinetest01'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def is_yes_no_question(question):
    """Check if a question is a yes/no question."""
    return "Does the solution meet the goal?" in question

def clean_question(question):
    """Remove unwanted lines such as URLs, dates, times, and pagination."""
    # Remove URLs
    question = re.sub(r'https?://\S+', '', question)
    # Remove dates and times (e.g., 22/07/2024, 00:04)
    question = re.sub(r'\d{2}/\d{2}/\d{4}, \d{2}:\d{2}', '', question)
    # Remove pagination lines (e.g., 2/5)
    question = re.sub(r'\d+/\d+', '', question)
    # Remove form feed characters
    question = question.replace('\f', '')
    # Remove extra new lines and spaces
    question = re.sub(r'\n\s*\n', '\n', question).strip()
    return question

def extract_text_from_pdf(file_path):
    """Extract text from the PDF file."""
    return extract_text(file_path)

def extract_images_from_pdf(file_path):
    """Extract page numbers containing images from the PDF file."""
    doc = fitz.open(file_path)
    pages_with_images = set()
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        if image_list:
            pages_with_images.add(page_num + 1)  # Page numbers start from 1
    return pages_with_images

def read_questions_from_text(text, pages_with_images):
    """Read questions from the extracted text."""
    # Split questions based on "Question #"
    questions = re.split(r'Question #\d+', text)
    # Remove the first split part which doesn't contain a question
    cleaned_questions = [clean_question(q) for q in questions[1:]]
    # Categorize questions by page number
    questions_by_page = {page_num + 1: [] for page_num in range(len(cleaned_questions))}
    for i, question in enumerate(cleaned_questions):
        questions_by_page[i + 1].append(question)
    return questions_by_page

def categorize_questions(questions_by_page, pages_with_images):
    """Categorize questions into multiple-choice, yes/no, and image-based."""
    mcq_questions = []
    yes_no_questions = []
    image_questions = []
    for page_num, questions in questions_by_page.items():
        for question in questions:
            if page_num in pages_with_images:
                image_questions.append(question)
            elif is_yes_no_question(question):
                yes_no_questions.append(question)
            else:
                mcq_questions.append(question)
    return mcq_questions, yes_no_questions, image_questions

def save_questions_to_db(mcq_questions, yes_no_questions, image_questions):
    """Save questions to the database."""
    for question in mcq_questions:
        q = Question(question_text=question, question_type='MCQ')
        session.add(q)
        session.commit()

    for question in yes_no_questions:
        q = Question(question_text=question, question_type='YES_NO')
        session.add(q)
        session.commit()

    for question in image_questions:
        q = Question(question_text=question, question_type='IMAGE')
        session.add(q)
        session.commit()
        iq = ImageQuestion(question_id=q.id)
        session.add(iq)
        session.commit()

def main():
    input_file = 'ETAZ900-91.pdf'
    mcq_file = 'mcq_questions.txt'
    yes_no_file = 'yes_no_questions.txt'
    image_questions_file = 'image_questions.txt'

    # Extract text and images from the PDF
    text = extract_text_from_pdf(input_file)
    pages_with_images = extract_images_from_pdf(input_file)
    
    questions_by_page = read_questions_from_text(text, pages_with_images)
    mcq_questions, yes_no_questions, image_questions = categorize_questions(questions_by_page, pages_with_images)

    # Save questions to files
    write_questions(mcq_file, mcq_questions)
    write_questions(yes_no_file, yes_no_questions)
    write_questions(image_questions_file, image_questions)
    
    # Save questions to database
    save_questions_to_db(mcq_questions, yes_no_questions, image_questions)
    
    print(f'Written {len(mcq_questions)} MCQ questions to {mcq_file}')
    print(f'Written {len(yes_no_questions)} yes/no questions to {yes_no_file}')
    print(f'Written {len(image_questions)} image-based questions to {image_questions_file}')

if __name__ == '__main__':
    main()
