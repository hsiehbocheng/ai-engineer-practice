import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote, urlparse, parse_qsl, urlencode, urlunparse

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
)
from linebot.v3.messaging.models import (
    StickerMessage,
    ShowLoadingAnimationRequest,
    PushMessageRequest,
    FlexMessage,
    FlexContainer,
)
from dotenv import load_dotenv
from utils.utils import normalize_llm_text, event_hour_yyyymmddhh

# -----------------------------------------------------------------------------
# 基本設定
# -----------------------------------------------------------------------------
load_dotenv()
app = Flask(__name__)

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
llm_api_base = os.getenv("LLM_API_BASE", "http://localhost:8000")

# 背景執行緒池（依你的流量調整）
executor = ThreadPoolExecutor(max_workers=8)

# 共用 requests Session（連線重用、較省時）
_requests_session = requests.Session()


def _ensure_valid_action_uri(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return f"https://maps.google.com/maps?q={quote(url, safe='')}"
        safe_path = quote(parsed.path, safe='/-._~')
        encoded_query = urlencode(
            parse_qsl(parsed.query, keep_blank_values=True),
            doseq=True,
            quote_via=quote
        )
        return urlunparse((parsed.scheme, parsed.netloc, safe_path, parsed.params, encoded_query, parsed.fragment))
    except Exception:
        return f"https://maps.google.com/maps?q={quote(url, safe='')}"


def call_agent(user_id: str, query: str) -> str:
    """
    呼叫你的 LLM 服務。
    - timeout 拆成 (connect, read)：避免卡在連線建立。
    - 回傳純文字，失敗則回覆友善訊息。
    """
    try:
        r = _requests_session.get(
            f"{llm_api_base}/chat",
            params={"user_id": user_id, "query": query}
        )
        r.raise_for_status()
        return r.text.strip()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"LLM 呼叫失敗：{e}")
        return "有一些問題發生 ... 請稍後再試"

def _parking_flex_messages_wrapper(data: list[dict]) -> list[dict]:
    bubbles = []
    for item in data:
        google_maps_url = item.get('google_maps_url', '')
        parking_name = item.get('parking_name', '停車場')

        encoded_name = quote(parking_name, safe='')
        google_maps_url = google_maps_url or f"https://maps.google.com/maps?q={encoded_name}"
        google_maps_url = _ensure_valid_action_uri(google_maps_url)

        bubble = {
            'type': 'bubble',
            'hero': {
                'type': 'image',
                'url': 'https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png',
                'size': 'full',
                'aspectRatio': '20:13',
                'aspectMode': 'cover'
            },
            'body': {
                'type': 'box',
                'layout': 'vertical',
                'contents': [
                    {'type': 'text', 'text': item.get('parking_name', '停車場'), 'weight': 'bold', 'size': 'xl'},
                    {'type': 'text', 'text': f"💫 類型：{item.get('parking_type', '-')}", 'size': 'sm', 'color': '#666666'},
                    {'type': 'text', 'text': f"✅ 空位：{item.get('available_seats', '-')}", 'size': 'sm', 'color': '#666666'},
                    {'type': 'text', 'text': f"💰 費率：{item.get('parking_fee_description', '-')}", 'size': 'sm', 'color': '#666666'},
                ]
            },
            'footer': {
                'type': 'box', 'layout': 'vertical', 'contents': [
                    {'type': 'button', 'style': 'link', 'height': 'sm',
                     'action': {'type': 'uri', 'label': 'Google Map', 'uri': google_maps_url}}
                ]
            }
        }
        bubbles.append(bubble)
    return bubbles

def _toilet_flex_messages_wrapper(data: list[dict]) -> list[dict]:
    bubbles = []
    for item in data:
        toilet_name = item.get('toilet_name', '公廁')
        # 使用名稱或地址做為搜尋字串
        search_text = item.get('toilet_address') or toilet_name
        encoded = quote(search_text, safe='')
        google_maps_url = item.get('toilet_google_maps_url') or f"https://maps.google.com/maps?q={encoded}"
        google_maps_url = _ensure_valid_action_uri(google_maps_url)

        contents = [
            {'type': 'text', 'text': toilet_name, 'weight': 'bold', 'size': 'xl'},
        ]
        # 動態補上可用資訊
        if item.get('toilet_type'):
            contents.append({'type': 'text', 'text': f"🧻 類型：{item.get('toilet_type')}", 'size': 'sm', 'color': '#666666'})
        if item.get('toilet_distance'):
            contents.append({'type': 'text', 'text': f"📏 距離：{item.get('toilet_distance')}", 'size': 'sm', 'color': '#666666'})
        if item.get('toilet_address'):
            contents.append({'type': 'text', 'text': f"📍 地址：{item.get('toilet_address')}", 'size': 'sm', 'color': '#666666'})
        if item.get('toilet_available_seats'):
            contents.append({'type': 'text', 'text': f"🚽 廁所數量：{item.get('toilet_available_seats')}", 'size': 'sm', 'color': '#666666'})
        if item.get('toilet_accessible_seats'):
            contents.append({'type': 'text', 'text': f"♿ 無障礙：{item.get('toilet_accessible_seats')}", 'size': 'sm', 'color': '#666666'})
        if item.get('toilet_family_seats'):
            contents.append({'type': 'text', 'text': f"👨‍👩‍👧‍👦 親子：{item.get('toilet_family_seats')}", 'size': 'sm', 'color': '#666666'})

        bubble = {
            'type': 'bubble',
            'hero': {
                'type': 'image',
                'url': 'https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png',
                'size': 'full',
                'aspectRatio': '20:13',
                'aspectMode': 'cover'
            },
            'body': {
                'type': 'box',
                'layout': 'vertical',
                'contents': contents
            },
            'footer': {
                'type': 'box', 'layout': 'vertical', 'contents': [
                    {'type': 'button', 'style': 'link', 'height': 'sm',
                     'action': {'type': 'uri', 'label': 'Google Map', 'uri': google_maps_url}}
                ]
            }
        }
        bubbles.append(bubble)
    return bubbles

def get_structured_info_and_summary(user_id: str, query: str) -> tuple[dict, str]:
    """
    先呼叫 /chat 取得 llm_result，接著並行呼叫：
    - /get_agent_structure_response → 結構化資料（JSON）
    - /get_llm_summary → 摘要（純文字）
    """
    try:
        llm_result = call_agent(user_id, query)
        # 以併發方式同時呼叫兩個 endpoint，降低延遲
        with ThreadPoolExecutor(max_workers=2) as pool:
            f_struct = pool.submit(
                _requests_session.post,
                f"{llm_api_base}/get_agent_structure_response",
                data={"query": llm_result}
            )
            f_summary = pool.submit(
                _requests_session.post,
                f"{llm_api_base}/get_llm_summary",
                data={"query": llm_result}
            )

            struct_resp = f_struct.result()
            sum_resp = f_summary.result()

        struct_resp.raise_for_status()
        sum_resp.raise_for_status()

        structured = struct_resp.json()
        summary_text = sum_resp.text.strip()
        summary_text = normalize_llm_text(summary_text)
        return structured, summary_text
    except requests.exceptions.RequestException as e:
        app.logger.error(f"LLM 呼叫失敗：{e}")
        return {}, ""


def _push_text(user_id: str, text: str):
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=text)],
            )
        )

def _push_flex_message(user_id: str, alt_text: str, flex_contents: dict):
    try:
        with ApiClient(configuration) as api_client:
            flex_container = FlexContainer.from_dict(flex_contents)
            MessagingApi(api_client).push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[FlexMessage(alt_text=alt_text, contents=flex_container)],
                )
            )
    except Exception as e:
        app.logger.error(f"發送 FlexMessage 失敗：{e}")
        # 如果 FlexMessage 發送失敗，改用文字訊息
        _push_text(user_id, f"{alt_text}\n抱歉，無法顯示互動式介面，請稍後再試。")


def process_and_push_text(user_id: str, user_id_with_session: str, query: str):
    """
    背景任務：呼叫 LLM → 正規化 → Push 回使用者
    """
    answer = call_agent(user_id=user_id_with_session, query=query)
    answer = normalize_llm_text(answer)
    _push_text(user_id, answer)

def process_and_push_structured_info(user_id: str, user_id_with_session: str, query: str):
    """
    背景任務：取得結構化資訊（停車/廁所） → 發送 FlexMessage
    """
    try:
        structured, summary_text = get_structured_info_and_summary(user_id_with_session, query)
        parking_list = structured.get('parking_list') or []
        toilet_list = structured.get('toilet_list') or []
        
        if summary_text:
            _push_text(user_id, summary_text)

        sent_any = False
        if isinstance(parking_list, list) and len(parking_list) > 0:
            parking_bubbles = _parking_flex_messages_wrapper(parking_list)
            _push_flex_message(user_id, "停車場資訊", {'type': 'carousel', 'contents': parking_bubbles})
            sent_any = True
        if isinstance(toilet_list, list) and len(toilet_list) > 0:
            toilet_bubbles = _toilet_flex_messages_wrapper(toilet_list)
            _push_flex_message(user_id, "公廁資訊", flex_contents={'type': 'carousel', 'contents': toilet_bubbles})
            sent_any = True

        if not sent_any:
            _push_text(user_id, "抱歉，附近沒有找到停車場或公廁資訊。")

    except Exception as e:
        app.logger.error(f"處理結構化資訊失敗：{e}")
        _push_text(user_id, "抱歉，取得資訊時發生錯誤，請稍後再試。")


# -----------------------------------------------------------------------------
# Flask / LINE Webhook
# -----------------------------------------------------------------------------
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers.get("X-Line-Signature")

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    # 立刻回 200，避免 LINE 判定 webhook 超時（~2 秒）
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    hour_suffix = event_hour_yyyymmddhh(event.timestamp)
    user_id_with_session = f"{user_id}:{hour_suffix}"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loadingSeconds=60)
            )
        except Exception:
            app.logger.warning("show loading animation failed, continue ...")

    # 把重運算丟到背景（ThreadPoolExecutor）
    executor.submit(
        process_and_push_text,
        user_id,
        user_id_with_session,
        event.message.text,
    )


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    user_id = event.source.user_id
    hour_suffix = event_hour_yyyymmddhh(event.timestamp)
    user_id_with_session = f"{user_id}:{hour_suffix}"

    lat = event.message.latitude
    lon = event.message.longitude
    city = event.message.title
    address = event.message.address
    query = f"我的位置資訊是：緯度：{lat}, 經度：{lon} {city} {address} 附近"

    # 盡量別在這裡做耗時的事情（<= 2 秒就 return）
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 立刻回覆短訊息，避免 reply token 超時
        try:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="收到定位，停車寶來幫你找找目前最新資訊，可能要稍等一下下得斯 ... ϞϞ(๑⚈ ․̫ ⚈๑)∩")],
                )
            )
        except Exception as e:
            app.logger.warning(f"quick reply failed: {e}")
            
        # 顯示 loading（只是前端體感，與 webhook 逾時無關）
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loadingSeconds=60)
            )
        except Exception:
            app.logger.warning("show loading animation failed, continue ...")

    # 把停車場資訊處理丟到背景（ThreadPoolExecutor）
    executor.submit(process_and_push_structured_info, user_id, user_id_with_session, query)


if __name__ == "__main__":
    # 建議 production 用 WSGI/ASGI server（gunicorn/uvicorn）與反向代理
    app.run(debug=True)