import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Generator:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    def _build_prompt(self, query: str, contexts: list[str]) -> str:
        context_text = "\n".join(contexts)

        return f"""
You are a helpful assistant.

Answer the question using ONLY the context below.
If the answer is not present, say you don't know.

Context:
{context_text}

Question:
{query}
"""

    def generate(self, query: str, contexts: list[str]) -> str:
        prompt = self._build_prompt(query, contexts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"LLM call failed: {str(e)}"

    def stream_generate(self, query: str, contexts: list[str]):
        prompt = self._build_prompt(query, contexts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                stream=True,
            )

            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

        except Exception as e:
            yield f"\n\nLLM streaming failed: {str(e)}"