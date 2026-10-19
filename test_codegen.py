import ollama
import time

print("Testing Ollama connection...")
start = time.time()

try:
    response = ollama.chat(
        model='deepseek-coder:6.7b',
        messages=[
            {'role': 'user', 'content': 'Write pandas code to get the mean of column sales. Return only code.'}
        ],
        options={'temperature': 0.0},
    )
    elapsed = time.time() - start
    print(f"✅ Response received in {elapsed:.1f}s")
    print("-" * 40)
    print(response['message']['content'])
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Failed after {elapsed:.1f}s")
    print(f"Error type: {type(e).__name__}")
    print(f"Error: {e}")