from pydantic import BaseModel

class GenerateAudioRequest(BaseModel):
    text: str
    voice: str = "alloy"
    sample_rate: int = 44100

class GenerateAudioResponse(BaseModel):
    audio_url: str
    duration_seconds: float | None = None
