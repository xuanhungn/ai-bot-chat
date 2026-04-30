import requests

API_KEY = "your_key"

res = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "xin chào"}]
    }
)

print(res.status_code)
print(res.text)