from pydantic import BaseModel, Field
from typing import Optional, List


class MusicPlan(BaseModel):
    title: str = Field(..., description="Название трека")
    style_prompt: str = Field(..., description="Стилевой промпт для Suno")
    lyrics: str = Field(..., description="Текст песни или 'instrumental'")
    tags: List[str] = Field(default_factory=list, description="Теги жанра/стиля")
    duration_sec: Optional[int] = Field(None, description="Длительность в секундах")


class GenerateRequest(BaseModel):
    text: str = Field(..., description="Описание желаемой музыки пользователем")
    instrumental: bool = Field(default=False, description="Инструментальная композиция")
    duration_sec: Optional[int] = Field(None, description="Желаемая длительность в секундах")
