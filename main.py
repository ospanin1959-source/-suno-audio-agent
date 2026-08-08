from fastapi import FastAPI
from schemas import GenerateAudioRequest, GenerateAudioResponse
from suno_client import SunoClient
from qwen_agent import QwenAgent

app = FastAPI(title="Suno Agent")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Suno agent is running"}

@app.post("/generate", response_model=GenerateAudioResponse)
async def generate(req: GenerateAudioRequest):
    """Simple endpoint that uses QwenAgent to generate text and SunoClient to (placeholder) generate audio.
    These implementations are stubs — replace with real integrations.
    """
    agent = QwenAgent()
    suno = SunoClient()

    prompt = req.text
    generated_text = agent.generate_text(prompt)
    audio_bytes = suno.generate_audio(generated_text, voice=req.voice, sample_rate=req.sample_rate)
    audio_url = suno.upload_audio(audio_bytes)

    return {"audio_url": audio_url}
