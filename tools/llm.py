import os, json, re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def _extract_json(text: str) -> dict:
    # Grab the first JSON object in the output
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError(f"No JSON found in LLM output:\n{text}")
    return json.loads(m.group(0))

class LLM:
    def __init__(self, model: str = "gemini-flash-latest"):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model)

    def json(self, prompt: str, image_bytes: bytes | None = None) -> dict:
        if image_bytes is None:
            resp = self.model.generate_content(prompt)
        else:
            resp = self.model.generate_content([prompt, {"mime_type": "image/png", "data": image_bytes}])
        return _extract_json(resp.text)

# easy model swap:
# llm = LLM("gemini-2.0-flash")  # Different model
