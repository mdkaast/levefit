"""Интерфейс LLM-провайдера. Остальной код зависит только от LLMProvider, провайдер заменяем."""

import json
from typing import Protocol

import anthropic

from app.ai.prompt import SYSTEM_PROMPT
from app.ai.safety import InvalidAdjustment
from app.ai.schema import Adjustment
from app.config import settings


class AdjustmentUnavailable(Exception):
    """Модель недоступна, отказалась отвечать или вернула непригодный ответ."""


class LLMProvider(Protocol):
    model: str

    def generate_adjustment(self, snapshot: dict) -> Adjustment: ...


class AnthropicProvider:
    def __init__(self, model: str, timeout_s: float):
        self.model = model
        # Ключ приходит только из окружения (ANTHROPIC_API_KEY); в коде и логах его нет.
        self._client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key, timeout=timeout_s, max_retries=2
        )

    def generate_adjustment(self, snapshot: dict) -> Adjustment:
        try:
            response = self._client.messages.parse(
                model=self.model,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": json.dumps(snapshot, ensure_ascii=False),
                    }
                ],
                output_format=Adjustment,
            )
        except anthropic.APIError as exc:
            raise AdjustmentUnavailable(type(exc).__name__) from None
        except ValueError:  # ответ не прошёл разбор по схеме: пусть вызывающий повторит запрос
            raise InvalidAdjustment("response does not match the schema") from None
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise AdjustmentUnavailable("refusal or empty output")
        return response.parsed_output


def get_llm() -> LLMProvider:
    if not settings.anthropic_api_key:
        raise AdjustmentUnavailable("ANTHROPIC_API_KEY is not configured")
    return AnthropicProvider(settings.llm_model, settings.llm_timeout_s)
