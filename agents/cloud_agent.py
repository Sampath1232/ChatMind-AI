import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class CloudLLMAgent:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = "llama-3.3-70b-versatile"

    def generate(self, prompt):

        try:

            completion = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content":
                        "You are a helpful AI assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.7,
                max_tokens=500
            )

            return (
                completion
                .choices[0]
                .message
                .content
            )

        except Exception as e:

            return (
                f"Cloud AI Error: {str(e)}"
            )