from chatgpt import getChatGPTMessage
from decouple import config
from errors import InsufficientQuota
from fastapi import APIRouter, Header, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

router = APIRouter(
    prefix="/line",
    tags=["line"]
)

CHANNEL_SECRET = config("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = config("CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@router.post("/chatgpt")
async def chatgpt(request: Request, X_Line_Signature: str= Header(default=None)):
    #* X-Line-Signature header value
    #* get request body as text
    data = await request.body()
    body = data.decode('utf-8')
    
    #* handle webhook body
    try:
        handler.handle(body, X_Line_Signature)
    except InvalidSignatureError:
        raise HTTPException(400,"Invalid signature. Please check your channel access token/channel secret.")
    except InsufficientQuota:
        reply_token = body['events'][0]['replyToken']
        line_bot_api.reply_message(reply_token, TextSendMessage(text="current quota has exceeded"))
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    fake_metioned = "@NiCeChatGPT"
    t = event.message.text
    if t.startswith("@NiCeChatGPT"):
        #* call chatGPT function
        q = t.removeprefix(fake_metioned).strip()
        reply = getChatGPTMessage(q)
        while reply.startswith("\n"):
            reply = reply.removeprefix("\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply))