from __future__ import annotations

import os


class AIAssistant:
    def __init__(self, provider: str = "openai") -> None:
        self.provider = provider

    def is_configured(self) -> bool:
        if self.provider == "google":
            return bool(os.getenv("GOOGLE_API_KEY"))
        return bool(os.getenv("OPENAI_API_KEY"))

    def handle_command(self, command: str) -> str:
        if not self.is_configured():
            return "AI provider is not configured."
        return f"Received command: {command}"
