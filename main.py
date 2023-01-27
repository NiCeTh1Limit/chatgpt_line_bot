import requests, json
from fastapi import FastAPI, Header, Request, HTTPException
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from decouple import config
from errors import InsufficientQuota

CHANNEL_SECRET = config("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = config("CHANNEL_ACCESS_TOKEN")
OPEN_API_KEY = config("OPEN_API_KEY")

app = FastAPI()

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request, X_Line_Signature: str= Header(default=None)):
    #* X-Line-Signature header value
    #* get request body as text
    # body = await request.json()
    data = await request.body()
    body = data.decode('utf-8')
    # print(body)
    
    # handle webhook body
    try:
        # raise InsufficientQuota
        handler.handle(body, X_Line_Signature)
    except InvalidSignatureError:
        raise HTTPException(400,"Invalid signature. Please check your channel access token/channel secret.")
    except InsufficientQuota:
        reply_token = body['events'][0]['replyToken']
        line_bot_api.reply_message(reply_token, TextSendMessage(text="current quota has exceeded"))
    return "OK"

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
    # print(res)
    # print(res.text)
    if res.status_code!=200: raise InsufficientQuota
    res = res.json()
    reply = res['choices'][0]['text']
    return reply

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    fake_metioned = "@NiCeChatGPT"
    t = event.message.text
    if t.startswith("@NiCeChatGPT"):
        #* call chatGPT function
        q = t.removeprefix(fake_metioned).strip()
        reply = getChatGPTMessage(q)
        print(reply)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))
