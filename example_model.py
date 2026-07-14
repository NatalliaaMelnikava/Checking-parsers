import json
import asyncio
import os
from output import OrderExtractionSchema
from extractor import Extractor
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

async def main():
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        openai_api_key="EMPTY",
        base_url=os.getenv("MODEL_BASE_URL"),
    )

    order_extractor = Extractor(llm=llm, tool_model=OrderExtractionSchema)
    
    order_extractor.setup_prompt("""
You are an expert Logistics AI Assistant.
**Task:** Extract structured logistics data from a JSON object containing 'paragraphs' and 'tables'.

**CRITICAL INSTRUCTIONS:**
1. **INTEGRATION:** You must combine data from BOTH 'paragraphs' and 'tables'. 
   - Tables contain structured fields (like weights, places, codes).
   - Paragraphs contain unstructured business logic (like transport requirements, notes, type of cargo).
   - If a field is not in the table, look for it in the 'paragraphs' list.
2. **HANDLING PLACEHOLDERS:** If the document uses placeholders (e.g., 'XXX', 'XX', '______', '_______'), return `null` or `NOT_FOUND`. DO NOT guess numbers.
3. **LOGISTICS EXTRACTION RULES:**
   - **Dates:** Always look for date patterns (DD.MM.YYYY) in the first 10 paragraphs.
   - **Transport Requirements:** Extract 'Вид транспорта', 'Тип загрузки', 'Техническое оснащение' from the text paragraphs if they are not in the table.
   - **Route:** The route is often split across multiple paragraphs. Assemble it chronologically.
   - **Booleans:** Explicitly check paragraphs for keywords like "нельзя перецеплять", "два водителя", "не перегружать". This info is usually in text, not tables.

**Example of Reasoning:**
- Input: "Вид транспорта: Автомобильный сборная доставка" in paragraphs.
- Output: Set `transport_reqs.trailer_type` to "Автомобильный сборная доставка".

**Final constraint:** If a value is genuinely missing, use `null`. Do not invent info.
""")
    
    order_extractor.create_extractor()
    
    file_path = ""
    
    if not os.path.exists(file_path):
        print(f"[!] Файл не найден: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        # Загружаем данные в виде словаря
        data_from_json = json.load(f)
        
    raw_text_from_camelot = json.dumps(data_from_json, ensure_ascii=False)
    
    print(f"Отправляем данные из {file_path} в LLM")
    final_data = await order_extractor.extract_order_data(raw_text_from_camelot)
    
    print("ИЗВЛЕЧЕННЫЕ ДАННЫЕ")
    print(json.dumps(final_data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())