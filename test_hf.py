import requests

url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

headers = {
    "Authorization": "Bearer YOUR_HF_TOKEN"
}

r = requests.post(url, headers=headers, json={"inputs": "hello"})

print("STATUS:", r.status_code)
print("TEXT:", r.text)
print("FINAL URL:", r.url)