import requests

from docx import Document

# 仅适用于 .docx
doc = Document('D:/简历5.15.docx')
for paragraph in doc.paragraphs:
    print(paragraph.text)
print(f"\n内联图片数量: {len(doc.inline_shapes)}")




