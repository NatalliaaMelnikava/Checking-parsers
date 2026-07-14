from tika_pdf_rg import DocumentLoader

source_data = ""

loader = DocumentLoader(source_data)
loader.load_text()
chunks = loader.split_text()

for i in chunks.__iter__():
    #print("Первый кусок:")
    print(i, end="\n\n")
