import os
from openai import OpenAI


class QueryDecomposer:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

    def decompose(self, query):

        prompt = f"""
Break the user query into smaller search queries.

Return 3 search queries maximum.

Query:
{query}
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        queries = text.split("\n")

        return [q.strip("- ") for q in queries if q.strip()]