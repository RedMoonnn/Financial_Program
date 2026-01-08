from openai import OpenAI

client = OpenAI(
    base_url="http://192.168.211.1:8045/v1", api_key="sk-a0a5b844ce4444289a93e6835bc41296"
)

response = client.chat.completions.create(
    model="gemini-3-flash", messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
