import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


class ReasoningModel:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = "llama-3.3-70b-versatile"

    def generate(self, query, contexts):

        context_text = "\n\n".join(contexts)

        prompt = f"""
Use step-by-step reasoning to answer the question.

Context:
{context_text}

Question:
{query}

Explain your reasoning clearly.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )

        return response.choices[0].message.content