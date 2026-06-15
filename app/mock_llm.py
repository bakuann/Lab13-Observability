from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE
from .pii import summarize_text
from .tracing import langfuse_context, observe


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(name="llm-generation", as_type="generation", capture_input=False, capture_output=False)
    def generate(self, prompt: str) -> FakeResponse:
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4
        answer = self._answer_for_prompt(prompt)
        response = FakeResponse(
            text=answer,
            usage=FakeUsage(input_tokens, output_tokens),
            model=self.model,
        )
        langfuse_context.update_current_generation(
            input={"prompt_preview": summarize_text(prompt)},
            output={"answer_preview": summarize_text(answer)},
            model=self.model,
            usage_details={"input": input_tokens, "output": output_tokens},
            metadata={"cost_spike": STATE["cost_spike"]},
        )
        return response

    @staticmethod
    def _answer_for_prompt(prompt: str) -> str:
        if "Refunds are available" in prompt:
            return "Refunds are available within 7 days when you provide proof of purchase."
        if "Metrics detect incidents" in prompt:
            return "Metrics detect incidents, traces localize the slow or failing step, and logs explain the root cause."
        if "Do not expose PII" in prompt:
            return "Sensitive PII must not appear in logs; store only sanitized summaries and hashed identifiers."
        return (
            "Use metrics to detect abnormal behavior, traces to localize it, and structured logs "
            "to explain the root cause while keeping sensitive PII redacted."
        )
