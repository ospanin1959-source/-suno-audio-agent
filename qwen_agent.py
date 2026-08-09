import os
import json
import re
from typing import Optional, Dict, Any

from openai import OpenAI


def make_music_plan(user_text: str, instrumental: bool, duration_sec: Optional[int]) -> Dict[str, Any]:
    """
    Генерирует музыкальный план через Qwen API.
    
    Args:
        user_text: Описание желаемой музыки от пользователя
        instrumental: Флаг инструментальной композиции
        duration_sec: Желаемая длительность в секундах
    
    Returns:
        Словарь с полями: title, style_prompt, lyrics, tags, duration_sec
    """
    api_key = os.getenv("QWEN_API_KEY")
    base_url = os.getenv("QWEN_BASE_URL")
    model = os.getenv("QWEN_MODEL", "qwen")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    system_prompt = (
        "Ты музыкальный продюсер и prompt-engineer для Suno. "
        "Твоя задача — создать качественный музыкальный план на основе описания пользователя. "
        "Верни ТОЛЬКО валидный JSON без markdown-разметки, без пояснений. "
        "JSON должен содержать поля: title, style_prompt, lyrics, tags, duration_sec.\n"
        "- title: короткое название трека (строка)\n"
        "- style_prompt: подробное описание стиля для генерации (строка)\n"
        "- lyrics: текст песни или 'instrumental' если инструментальная композиция (строка)\n"
        "- tags: список тегов жанра/стиля (массив строк)\n"
        "- duration_sec: длительность в секундах (число или null)"
    )
    
    user_prompt = f"Создай музыкальный план для: {user_text}. {'Инструментальная композиция.' if instrumental else ''}{' Длительность: ' + str(duration_sec) + ' секунд.' if duration_sec else ''}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content.strip()
    
    # Устойчивый парсинг JSON из ответа модели
    return parse_json_response(content)


def parse_json_response(content: str) -> Dict[str, Any]:
    """
    Устойчивый парсинг JSON из ответа модели.
    Пытается извлечь JSON даже если он обёрнут в markdown или содержит лишний текст.
    """
    # Удаляем markdown-блоки кода
    content = re.sub(r'^```json\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```\s*', '', content, flags=re.MULTILINE)
    content = content.strip()
    
    # Пытаемся найти JSON между фигурными скобками
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group(0)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Не удалось распарсить JSON из ответа модели: {e}. Ответ: {content}")
