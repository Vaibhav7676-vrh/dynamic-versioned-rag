import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Generator:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        """
        Groq uses an OpenAI-compatible API.
        We only change base_url and API key.
        """
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # graceful fallback (VERY IMPORTANT for production)
            return f"LLM call failed: {str(e)}"
