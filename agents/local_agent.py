import requests

class LocalLLMAgent:

    def generate(self, prompt):

        try:

            response = requests.post(
                "http://localhost:11434/api/generate",

                json={
                    "model": "phi3",
                    "prompt": prompt,
                    "stream": False
                }
            )

            data = response.json()

            return data["response"]

        except Exception as e:

            return f"Local AI Error: {str(e)}"