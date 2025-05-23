# --- 您的其他匯入和常數定義 ---
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo 
from typing import Optional, Set
from api.database import db_manager 
from dotenv import load_dotenv

load_dotenv()

ALLOWED_SIZES: Set[str] = {"S", "M", "L", "XL", "XXL"}
SIZE_DELIMITER: str = "/"
Base = declarative_base()

# --- 共用的驗證邏輯函式 ---
def shared_size_validation_logic(
    value: Optional[str],
    field_name_for_error: str, # 用於錯誤訊息
    allowed_sizes_set: Set[str],
    delimiter: str
) -> Optional[str]:
    if value is None or value.strip() == "":
        return None
    raw_parts = value.split(delimiter)
    cleaned_parts = [part.strip() for part in raw_parts if part.strip()]
    if not cleaned_parts and value.strip() != "":
        raise ValueError(
            f"{field_name_for_error} 字串 '{value}' 格式無效，只包含分隔符號或無效字元。"
        )
    if not cleaned_parts:
        return None
    validated_unique_sizes = set()
    for part in cleaned_parts:
        if part not in allowed_sizes_set:
            raise ValueError(
                f"在 {field_name_for_error} 字串 '{value}' 中發現無效尺寸 '{part}'。允許的尺寸為: {sorted(list(allowed_sizes_set))}。"
            )
        if part in validated_unique_sizes:
            raise ValueError(
                f"在 {field_name_for_error} 字串 '{value}' 中發現重複尺寸 '{part}'。"
            )
        validated_unique_sizes.add(part)
    if not validated_unique_sizes:
        return None
    return delimiter.join(sorted(list(validated_unique_sizes)))



# --- SQLAlchemy 模型 Product ---
class Product(Base):
    __tablename__ = 'items'
    name = Column(String(255), nullable=False)
    code = Column(String(50), primary_key=True, index=True, nullable=False)
    category = Column(String(100), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    inventory = Column(Integer, nullable=False)
    size = Column(String(100), nullable=True)
    color = Column(String(255), nullable=True)

# --- Pydantic 模型 ---
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    unit_price: float = Field(..., gt=0)
    inventory: int = Field(..., ge=0)
    size: Optional[str] = Field(
        'S',
        max_length=100,
        description=(
            f"可用尺寸，使用 '{SIZE_DELIMITER}' 分隔 (例如: 'S/M/L')。\n"
            f"允許的個別尺寸有: {(list(ALLOWED_SIZES))}。\n"
            "不允許重複。若留空或不提供此欄位，則表示無特定尺寸。"
        )
    )
    color: Optional[str] = Field('red', max_length=255)

    @field_validator('size', mode='before')
    def validate_base_sizes(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:

        # 呼叫共用邏輯
        return shared_size_validation_logic(v, info.field_name, ALLOWED_SIZES, SIZE_DELIMITER)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    unit_price: Optional[float] = Field(None, gt=0)
    inventory: Optional[int] = Field(None, ge=0)
    size: Optional[str] = Field(
        None,
        max_length=100,
        description=(
            f"可用尺寸，使用 '{SIZE_DELIMITER}' 分隔 (例如: 'S/M/L')。\n"
            f"允許的個別尺寸有: {sorted(list(ALLOWED_SIZES))}。\n"
            "不允許重複。若留空或不提供此欄位，則表示無特定尺寸。"
        )
    )
    color: Optional[str] = Field(None, max_length=255)

    # 在 ProductUpdate 中也呼叫共用的驗證邏輯
    @field_validator('size', mode='before')
    def validate_update_sizes(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        # 呼叫共用邏輯
        return shared_size_validation_logic(v, info.field_name, ALLOWED_SIZES, SIZE_DELIMITER)

class ProductResponse(ProductBase):
    class Config:

        from_attributes = True # Pydantic V2


Base.metadata.create_all(bind=db_manager.engine)
