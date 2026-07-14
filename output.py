from typing import List, Optional
from pydantic import BaseModel, Field

class RoutePoint(BaseModel):
    """Структура для описания одной точки в логистическом маршруте следования груза."""
    point_type: str = Field(description="Тип: 'загрузка', 'затаможка', 'растаможка', 'выгрузка', 'промежуточная_точка'.")
    location: str = Field(description="Страна, город и точный адрес. Включая названия таможни или СВХ.")
    date_time: Optional[str] = Field(description="Дата и/или время для данной точки маршрута.")

class DangerousGoods(BaseModel):
    """Блок метаданных об опасном грузе (ADR)."""
    is_dangerous: bool = Field(description="Установить true, если груз классифицируется как опасный (ADR).")
    un_number: Optional[str] = Field(description="Номер ООН (UN number). Например, '1203'.")
    adr_class: Optional[str] = Field(description="Класс опасности груза.")
    packaging_group: Optional[str] = Field(description="Группа упаковки.")

class TransportRequirements(BaseModel):
    """Технические требования к транспортному средству для выполнения рейса."""
    trailer_type: Optional[str] = Field(description="Тип кузова (например: стандарт, мега, реф, тент, изотерма).")
    loading_type: Optional[str] = Field(description="Тип загрузки (например: верхняя, боковая, задняя).")
    tech_equipment: Optional[str] = Field(description="Техническое оснащение: ремни, цепи, коврики и т.д.")
    reefer_conditions: Optional[str] = Field(description="Для рефа: требуемый режим работы и температура.")
    oversized_conditions: Optional[str] = Field(description="Для негабарита: свес, уширение, широкий тент.")

class OrderExtractionSchema(BaseModel):
    """Главная структура для извлечения бизнес-данных из логистической заявки."""
    order_number: Optional[str] = Field(description="Номер заявки / поручения экспедитору.")
    customer_name: Optional[str] = Field(description="Наименование Заказчика (название компании).")
    loading_date_main: Optional[str] = Field(description="Общая дата загрузки, указанная в шапке заявки.")
    freight_rate_amount: Optional[float] = Field(description="Ставка (фрахт). Извлечь только числовое значение.")
    freight_rate_currency: Optional[str] = Field(description="Валюта ставки. Если отсутствует, вернуть 'NOT_FOUND'.")
    
    cargo_description: Optional[str] = Field(description="Детальное текстовое описание наименования груза.")
    weight_and_dimensions: Optional[str] = Field(description="Сырая строка с весом и габаритами из документа.")
    places_count: Optional[str] = Field(description="Количество грузовых мест.")
    cargo_value: Optional[str] = Field(description="Объявленная стоимость груза.")
    sanctions_info: Optional[str] = Field(description="Информация о санкционном контроле.")
    dangerous_goods_info: DangerousGoods = Field(description="Блок информации об опасном грузе (ADR).")

    transport_reqs: TransportRequirements = Field(description="Требования к транспорту, загрузке и оснащению.")
    route: List[RoutePoint] = Field(description="Массив всех точек маршрута от загрузки до выгрузки.")

    documents_required: Optional[str] = Field(description="Требуемые сопроводительные документы (CMR, Invoice и т.д.).")
    forwarder_notes: Optional[str] = Field(description="Примечание для экспедитора/водителя.")
    accounting_notes: Optional[str] = Field(description="Примечание для бухгалтерии: условия оплаты.")
    additional_info: Optional[str] = Field(description="Специфические условия (запрет перегруза, два водителя и т.д.).")
