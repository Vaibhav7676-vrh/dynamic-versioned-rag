import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Generator:
    def __init__(self, model: str = "openai/gpt-4.1-mini"):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.model = model

    def generate(self, query: str, contexts: list[str]) -> str:
        context_text = "\n".join(contexts)

        prompt = f"""
You are a helpful assistant.

Answer the question using ONLY the context below.
If the answer is not present, say you don't know.

Context:
{context_text}

Question:
{query}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()
