class SunoClient:
    """Placeholder client for Suno audio generation.

    Replace methods with real API calls to Suno's SDK or REST endpoints.
    """
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def generate_audio(self, text: str, voice: str = "alloy", sample_rate: int = 44100) -> bytes:
        """Stub: generate audio bytes for the given text.
        Currently returns empty bytes; integrate with real TTS.
        """
        # TODO: integrate with Suno API
        return b""

    def upload_audio(self, audio_bytes: bytes) -> str:
        """Stub: upload audio and return a URL or data URI.
        """
        if not audio_bytes:
            # Return a placeholder data URL for an empty response
            return "data:audio/wav;base64,"
        # TODO: implement upload to storage and return URL
        return "data:audio/wav;base64,PLACEHOLDER"
