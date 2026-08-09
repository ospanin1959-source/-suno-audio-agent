import os
from typing import Optional, Dict, Any

import httpx


class SunoAPIError(Exception):
    """Исключение для ошибок Suno API."""
    pass


class SunoClient:
    """Асинхронный клиент для Suno API."""
    
    def __init__(self):
        self.base_url = os.getenv("SUNO_API_BASE")
        self.api_key = os.getenv("SUNO_API_KEY")
        self.generate_path = os.getenv("SUNO_GENERATE_PATH", "/api/generate")
        self.status_path = os.getenv("SUNO_STATUS_PATH", "/api/status")
    
    @property
    def is_configured(self) -> bool:
        """Проверяет, настроен ли Suno API."""
        return bool(self.base_url and self.api_key)
    
    async def generate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправляет запрос на генерацию трека в Suno API.
        
        Args:
            plan: Музыкальный план с полями title, style_prompt, lyrics, tags, duration_sec
        
        Returns:
            Ответ API с job_id и статусом
        """
        if not self.is_configured:
            raise SunoAPIError("Suno API не настроен: проверьте переменные окружения SUNO_API_BASE и SUNO_API_KEY")
        
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{self.generate_path}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "title": plan.get("title", ""),
                "prompt": plan.get("style_prompt", ""),
                "lyrics": plan.get("lyrics", ""),
                "tags": plan.get("tags", []),
                "duration": plan.get("duration_sec")
            }
            
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise SunoAPIError(f"Ошибка HTTP при генерации: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise SunoAPIError(f"Ошибка запроса к Suno API: {str(e)}")
    
    async def status(self, job_id: str) -> Dict[str, Any]:
        """
        Получает статус генерации трека из Suno API.
        
        Args:
            job_id: ID задачи генерации
        
        Returns:
            Статус задачи с полями status, progress, audio_url (если готово)
        """
        if not self.is_configured:
            raise SunoAPIError("Suno API не настроен: проверьте переменные окружения SUNO_API_BASE и SUNO_API_KEY")
        
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{self.status_path}/{job_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise SunoAPIError(f"Ошибка HTTP при получении статуса: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise SunoAPIError(f"Ошибка запроса к Suno API: {str(e)}")
