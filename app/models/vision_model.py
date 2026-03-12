import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class VisionModel:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = "llava-v1.5-7b-4096-preview"

    def generate(self, query, image_path):

        with open(image_path, "rb") as img:
            base64_image = base64.b64encode(img.read()).decode("utf-8")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content