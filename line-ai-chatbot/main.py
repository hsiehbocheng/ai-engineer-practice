import os
import re
import requests
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent
)
from linebot.v3.messaging.models import (
    StickerMessage,
    TextMessage,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest
)
from dotenv import load_dotenv
from utils.utils import normalize_llm_text

load_dotenv()
app = Flask(__name__)
configuration = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
llm_api_base = os.getenv("LLM_API_BASE", 'http://localhost:8000')

def call_llm(user_id: str, query: str):
    try:
        r = requests.get(f"{llm_api_base}/chat", 
                         params={"user_id": user_id, "query": query}, 
                         timeout=30)
        r.raise_for_status()
        return r.text.strip()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling LLM API: {e}")
        return f"Error: {e}"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        
        user_id = event.source.user_id
        line_bot_api = MessagingApi(api_client)

        # show loading animation
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(
                    chat_id=user_id,
                    loadingSeconds=30
                )
            )
        except Exception as e:
            app.logger.warning('show loading animation faild, please wait ...')
        
        reply_text = call_llm(user_id=user_id, query=event.message.text)
        reply_text = normalize_llm_text(reply_text)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        
@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    with ApiClient(configuration) as api_client:
        user_id = event.source.user_id
        line_bot_api = MessagingApi(api_client)
        
        lat = event.message.latitude
        lon = event.message.longitude
        city = event.message.title
        address = event.message.address
        
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(
                    chat_id=user_id,
                    loadingSeconds=30
                )
            )
        except Exception as e:
            app.logger.warning('show loading animation faild, please wait ...')
        
        reply_text = call_llm(user_id=user_id, 
                              query=f"緯度：{lat}, 經度：{lon} {city} {address} 附近有什麼停車場")
        
        reply_text = normalize_llm_text(reply_text)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(debug=True)