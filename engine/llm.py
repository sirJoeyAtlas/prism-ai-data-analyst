import ollama
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
CODER_MODEL = os.getenv("CODER_MODEL", "deepseek-coder:1.3b")
HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

client = ollama.Client(host=HOST)


def chat(messages, model=None, temperature=0.1) -> str:
    model = model or MODEL
    response = client.chat(
        model=model,
        messages=messages,
        options={
            "temperature": temperature,
            "num_predict": 800,
            "num_ctx": 2048,  # Reduced from 4096
            "num_gpu": -1     # Force full GPU offload
}
    )
    return response["message"]["content"]


def generate_code(messages) -> str:
    return clean_code(chat(messages, model=CODER_MODEL, temperature=0.0))


def clean_code(text: str) -> str:
    text = text.strip()

    # Remove markdown fences anywhere
    text = text.replace("```python", "").replace("```", "")

    # Drop common chatter lines anywhere in the block
    chatter_starts = (
        "here is", "here's", "sure", "of course", "certainly",
        "this code", "the following", "below is", "note:",
        "explanation:", "output:", "in this code", "in the code",
        "this will", "the code will", "the chart",
    )
    lines = []
    for line in text.split("\n"):
        stripped = line.strip().lower()
        if any(stripped.startswith(c) for c in chatter_starts):
            continue
        lines.append(line)

    # Remove leading/trailing blanks
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # 🔑 Iteratively drop trailing lines until the code compiles
    while lines:
        candidate = "\n".join(lines)
        try:
            compile(candidate, "<generated>", "exec")
            return candidate
        except SyntaxError:
            lines.pop()

    return ""


def explain(messages) -> str:
    return chat(messages, model=MODEL, temperature=0.3)