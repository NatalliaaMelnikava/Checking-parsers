from typing import Any
from pydantic import BaseModel
from trustcall import create_extractor

class Extractor:
    """Class for retrieving logistics order information via LLM + TrustCall."""

    def __init__(self, llm: Any, tool_model: type[BaseModel]) -> None:
        """Initializes the service with a language model and tool configuration."""
        self.llm = llm
        self.tool_model = tool_model
        self.extractor = None
        self.prompt = None

    def setup_prompt(self, prompt_text: str | None = None) -> (str | None):
        """Sets the prompt text and returns it."""
        self.prompt = prompt_text
        return self.prompt

    def create_extractor(self) -> Any:
        """Creates and assigns an extractor using the configured language model and tools."""
        self.extractor = create_extractor(
            self.llm,
            tools=[self.tool_model],
            tool_choice="any",
            enable_inserts=True,
        )
        return self.extractor

    async def extract_order_data(self, text: str) -> dict:
        """
        Универсальная функция для извлечения всех данных заявки.
        Принимает текст, возвращает словарь по схеме.
        """
        messages_for_parser = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": text},
        ]
        
        try:
            # Вызываем LLM
            res = await self.extractor.ainvoke({"messages": messages_for_parser})
            
            # Получаем ответ от TrustCall
            extracted_model = res["responses"][0]
            
            if hasattr(extracted_model, "model_dump"):
                return extracted_model.model_dump()
            elif hasattr(extracted_model, "dict"):
                return extracted_model.dict() # Для старых версий Pydantic
            elif isinstance(extracted_model, dict):
                return extracted_model
            else:
                return {"error": f"Неизвестный формат ответа: {type(extracted_model)}"}

        except Exception as e:
            return {"error": f"Failed to extract order data: {str(e)}"}