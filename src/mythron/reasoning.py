"""MYTHRON Phase 1 — Reasoning core.

Thin wrapper around Google Gemini API. Single-turn prompt -> response.
Default model: gemini-3.6-flash.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.6-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 2048


def load_api_key() -> str:
    """Load GEMINI_API_KEY from environment or .env file."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if len(key) >= 20:
        return key
    env_path = Path(__file__).parent.parent.parent / ".env"
    if not env_path.exists():
        raise RuntimeError(f".env not found at {env_path}")
    env = {}
    for line in env_path.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    key = env.get("GEMINI_API_KEY", "")
    if len(key) < 20:
        raise RuntimeError(f"API key too short ({len(key)} chars)")
    return key


class ReasoningCore:
    """AI reasoning core for MYTHRON. Wraps Google Gemini API."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        client=None,
    ) -> None:
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._api_key = api_key or load_api_key()
        self._client = client or genai.Client(api_key=self._api_key)

    def reason(self, prompt: str) -> str:
        """Send prompt to LLM, return text response."""
        if not prompt or not prompt.strip():
            raise ValueError("prompt must be non-empty")
        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini API call failed: {exc}") from exc
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned empty response")
        return text


def main() -> int:
    """CLI smoke test for the reasoning core."""
    print("=== MYTHRON Reasoning Core — smoke test ===")
    core = ReasoningCore()
    print(f"Model: {core.model}")
    print(f"Temperature: {core.temperature}")
    print(f"Max output tokens: {core.max_output_tokens}")
    print()
    prompt = "Reply with exactly: HELLO FROM MYTHRON"
    print(f"Prompt: {prompt}")
    print()
    print("Response:")
    print(core.reason(prompt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
