import os, dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from linebot.v3 import WebhookHandler                    # 核心解析器
from linebot.v3.messaging import (                       # 同步客戶端
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

dotenv.load_dotenv()  # 讀取 .env

app = FastAPI()
conf     = Configuration(access_token=os.getenv("LINE_ACCESS_TOKEN"))
handler  = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.post("/webhook")
async def webhook(req: Request, bg: BackgroundTasks):
    body = await req.body()
    try:
        handler.handle(body.decode(), req.headers.get("X-Line-Signature", ""))
    except InvalidSignatureError:
        raise HTTPException(400, "Bad signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event: MessageEvent, bg: BackgroundTasks):
    def _reply():
        with ApiClient(conf) as client:
            api = MessagingApi(client)
            api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"你說：{event.message.text}")]
                )
            )
    # 一律放背景，避免阻塞 webhook 回應
    bg.add_task(_reply)