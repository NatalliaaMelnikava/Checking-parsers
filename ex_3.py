import json
import os
from cam_pdf import PDFExtractor

def main():
    source_data = ""

    if not os.path.exists(source_data):
        print(f"[!] Файл не найден: {source_data}")
        print("Убедись, что путь указан верно.")
        return

    try:
        print(f"[*] Начинаем обработку файла: {source_data}")
        
        loader = PDFExtractor(source_data)
         
        result = loader.load(flavor='lattice') 

        print("РЕЗУЛЬТАТЫ ПАРСИНГА")
        print(f"Всего параграфов: {len(result['paragraphs'])}")
        print(f"Всего таблиц: {len(result['tables'])}")
        print(f"Длина сырого текста (символов): {len(result['raw_text'])}")
        print("-" * 40)

        if result['tables']:
            print("\n[*] Структура первой найденной таблицы:")
            print(json.dumps(result['tables'][0], indent=4, ensure_ascii=False))
        else:
            print("\n[!] Таблицы в документе не найдены.")

        output_file = "extracted_prime_2.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"\n[+] Полные данные успешно сохранены в файл: {output_file}")

    except Exception as e:
        print("\n[x] Произошла ошибка в процессе парсинга:")
        print(f"{type(e).__name__}: {e}")

if __name__ == "__main__":
    main()