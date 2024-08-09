import re

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

def read_questions(file_path):
    """Read questions from the text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Split questions based on "Question #"
    questions = re.split(r'Question #\d+', content)
    # Remove the first split part which doesn't contain a question
    return [clean_question(q) for q in questions[1:]]

def write_questions(file_path, questions):
    """Write questions to a text file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        for question in questions:
            file.write(question.strip() + "\n\n")

def categorize_questions(questions):
    """Categorize questions into multiple-choice and yes/no."""
    mcq_questions = []
    yes_no_questions = []
    for question in questions:
        if is_yes_no_question(question):
            yes_no_questions.append(question)
        else:
            mcq_questions.append(question)
    return mcq_questions, yes_no_questions

def main():
    input_file = 'ETAZ900-91.txt'
    mcq_file = 'mcq_questions01.txt'
    yes_no_file = 'yes_no_questions01.txt'

    questions = read_questions(input_file)
    mcq_questions, yes_no_questions = categorize_questions(questions)

    write_questions(mcq_file, mcq_questions)
    write_questions(yes_no_file, yes_no_questions)
    print(f'Written {len(mcq_questions)} MCQ questions to {mcq_file}')
    print(f'Written {len(yes_no_questions)} yes/no questions to {yes_no_file}')

if __name__ == '__main__':
    main()
