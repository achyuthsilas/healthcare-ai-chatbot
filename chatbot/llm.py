"""
LLM client — wraps the Groq API (free tier, fast Llama inference).

Get your free API key at https://console.groq.com/keys
"""
import os
from typing import Iterator, List, Dict

from groq import Groq


SYSTEM_PROMPT = """You are a helpful, careful healthcare information assistant.

Your responsibilities:
- Provide clear, evidence-based general health information.
- Always remind users that you are not a substitute for a licensed clinician.
- Recommend seeing a doctor for diagnosis, prescriptions, or anything serious.
- For emergency symptoms (chest pain, stroke signs, severe bleeding, suicidal
  thoughts, difficulty breathing), urge the user to call emergency services
  immediately.
- Never invent dosages, drug interactions, or specific treatment plans.
- Be empathetic and use plain language.

If the user provides relevant context from the knowledge base below, prefer it
over your general knowledge when answering."""


# Available free Groq models (as of 2026):
#   "llama-3.3-70b-versatile"  - best quality, recommended default
#   "llama-3.1-8b-instant"     - fastest, lighter model
#   "gemma2-9b-it"             - Google's Gemma alternative
# See https://console.groq.com/docs/models for the current list.
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Copy .env.example to .env and add your key. "
                "Get a free key at https://console.groq.com/keys"
            )
        self.client = Groq(api_key=api_key)
        self.model = model

    def stream_response(
        self,
        messages: List[Dict[str, str]],
        context: str = "",
    ) -> Iterator[str]:
        """Stream a response from Groq given conversation history + RAG context."""
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\n--- Knowledge base context ---\n{context}\n--- End context ---"

        # Groq uses the OpenAI-style format: system message inside `messages`.
        api_messages = [{"role": "system", "content": system}]
        for m in messages:
            if m["role"] in ("user", "assistant"):
                api_messages.append({"role": m["role"], "content": m["content"]})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
