import ollama

response = ollama.chat(
    model='deepseek-coder:6.7b',
    messages=[{'role': 'user', 'content': 'Write Python pandas code to get the mean of column "sales"'}]
)
print("CODE MODEL:", response['message']['content'])

response2 = ollama.chat(
    model='qwen2.5:7b',
    messages=[{'role': 'user', 'content': 'Explain what a mean is in one sentence.'}]
)
print("\nGENERAL MODEL:", response2['message']['content'])