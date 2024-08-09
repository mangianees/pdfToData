import re
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text

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

def write_questions(file_path, questions):
    """Write questions to a text file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        for question in questions:
            file.write(question.strip() + "\n\n")

def main():
    input_file = 'ETAZ900-91.pdf'
    mcq_file = 'ETAZ900-91_mcq_questions.txt'
    yes_no_file = 'ETAZ900-91_yes_no_questions.txt'
    image_questions_file = 'ETAZ900-91_image_questions.txt'

    # Extract text and images from the PDF
    text = extract_text_from_pdf(input_file)
    pages_with_images = extract_images_from_pdf(input_file)
    
    questions_by_page = read_questions_from_text(text, pages_with_images)
    mcq_questions, yes_no_questions, image_questions = categorize_questions(questions_by_page, pages_with_images)

    write_questions(mcq_file, mcq_questions)
    write_questions(yes_no_file, yes_no_questions)
    write_questions(image_questions_file, image_questions)
    
    print(f'Written {len(mcq_questions)} MCQ questions to {mcq_file}')
    print(f'Written {len(yes_no_questions)} yes/no questions to {yes_no_file}')
    print(f'Written {len(image_questions)} image-based questions to {image_questions_file}')

if __name__ == '__main__':
    main()
