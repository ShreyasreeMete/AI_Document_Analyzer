"""Step 6: Groq LLM wrapper."""
from __future__ import annotations

import json
import re

from groq import Groq


class GroqLLM:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("Missing Groq API key.")
        self.client = Groq(api_key=api_key)
        self.model = model

    def ask(self, system: str, user: str, *, temperature: float = 0.2,
            max_tokens: int = 1500, json_mode: bool = False) -> str:
        kwargs = dict(
            model=self.model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content.strip()

    def ask_json(self, system: str, user: str, **kw) -> dict:
        raw = self.ask(system, user, json_mode=True, **kw)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", raw, re.S)
            if m:
                return json.loads(m.group(0))
            raise ValueError("The model did not return valid JSON. Try again.")
