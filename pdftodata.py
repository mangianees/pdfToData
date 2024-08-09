from pdfminer.high_level import extract_pages,extract_text

text = extract_text("ETAZ900-91.pdf")
# print(text)

with open("ETAZ900-91.txt", "w", encoding="utf-8") as file:
    file.write(text)