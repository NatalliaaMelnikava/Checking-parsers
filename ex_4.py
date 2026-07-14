import textract
text = textract.process("").decode()

print(text)