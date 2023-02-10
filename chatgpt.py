import requests
from decouple import config
from errors import InsufficientQuota

OPEN_API_KEY = config("OPEN_API_KEY")

def getChatGPTMessage(prompt:str):
    res = requests.post(
        'https://api.openai.com/v1/completions',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPEN_API_KEY}'
        },
        json = {
            'model': 'text-davinci-003',
            'prompt': prompt,
            'temperature': 0.4,
            'max_tokens': 300
        }
    )
    if res.status_code!=200: raise InsufficientQuota
    res = res.json()
    reply = res['choices'][0]['text']
    return reply