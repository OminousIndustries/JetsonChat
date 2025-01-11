# llm/ollama.py
import requests
import json

class OllamaClient:
    def __init__(self, url="http://localhost:11434/api/chat", model="llama3.2:1b", stream=True):
        self.url = url
        self.model = model
        self.stream = stream

    def query(self, user_text):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": user_text}
            ],
            "stream": self.stream
        }
        print("-> Sending user text to Ollama:\n", user_text)

        r = requests.post(self.url, json=payload, stream=self.stream)
        if r.status_code != 200:
            print("Error from Ollama:", r.status_code, r.text)
            return ""

        response_text = ""
        if self.stream:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if chunk.get("done"):
                        break
                    if "message" in chunk and chunk["message"].get("content"):
                        response_text += chunk["message"]["content"]
        else:
            data = r.json()
            if "message" in data and data["message"].get("content"):
                response_text = data["message"]["content"]

        return response_text.strip()
