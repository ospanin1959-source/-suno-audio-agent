import os
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from schemas import GenerateRequest, MusicPlan
from suno_client import SunoClient, SunoAPIError
from qwen_agent import make_music_plan

app = FastAPI(title="Suno Audio Agent")

# Хранилище для планов генерации (в памяти)
_jobs: Dict[str, Dict[str, Any]] = {}

suno_client = SunoClient()


@app.get("/")
async def healthcheck():
    """Healthcheck endpoint - показывает статус настройки Suno API."""
    suno_configured = suno_client.is_configured
    return {
        "status": "ok",
        "message": "Suno Audio Agent is running",
        "suno_configured": suno_configured
    }


@app.post("/prompt", response_model=MusicPlan)
async def create_prompt(req: GenerateRequest):
    """
    Создаёт музыкальный план через Qwen API.
    
    Принимает описание музыки и возвращает структурированный план
    с title, style_prompt, lyrics, tags, duration_sec.
    """
    try:
        plan_data = make_music_plan(
            user_text=req.text,
            instrumental=req.instrumental,
            duration_sec=req.duration_sec
        )
        return MusicPlan(**plan_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании музыкального плана: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка при создании плана: {str(e)}"
        )


@app.post("/generate")
async def generate(req: GenerateRequest):
    """
    Создаёт музыкальный план через Qwen и отправляет в Suno API для генерации.
    
    Возвращает job_id и план для последующей проверки статуса.
    """
    if not suno_client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Suno API не настроен. Проверьте переменные окружения SUNO_API_BASE и SUNO_API_KEY"
        )
    
    try:
        # Создаём музыкальный план через Qwen
        plan_data = make_music_plan(
            user_text=req.text,
            instrumental=req.instrumental,
            duration_sec=req.duration_sec
        )
        plan = MusicPlan(**plan_data)
        
        # Отправляем в Suno API
        result = await suno_client.generate(plan.dict())
        job_id = result.get("job_id", result.get("id", "unknown"))
        
        # Сохраняем план для справки
        _jobs[job_id] = {
            "plan": plan.dict(),
            "status": "pending"
        }
        
        return {
            "job_id": job_id,
            "plan": plan.dict()
        }
    except SunoAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Suno API недоступен: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании музыкального плана: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка при генерации: {str(e)}"
        )


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Получает статус генерации трека из Suno API.
    
    Возвращает текущий статус задачи (pending, processing, completed, failed).
    """
    if not suno_client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Suno API не настроен. Проверьте переменные окружения SUNO_API_BASE и SUNO_API_KEY"
        )
    
    try:
        status_result = await suno_client.status(job_id)
        return status_result
    except SunoAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Suno API недоступен: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса: {str(e)}"
        )
