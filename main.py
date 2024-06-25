from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

app = Flask(__name__)

# LINE bot的Channel Access Token和Channel Secret
LINE_BOT_API = '1PAiU+EnukB7WtoP+lZEZR1diJ7YfpnNJbvno/WW1PwdhBHeHtDAtzaN1hgGEp5YkQHXGMRaeeahCS6Nr1LTvqfRRheTlPdSs/NXRDxqSYFxihhg8nFzV9FRhTnx+cgG/RxWHLBfuxpsERqyOfDQ4wdB04t89/1O/w1cDnyilFU='
HANDLER = '910973d1cee8b1ee4407254e3ca5fb2d'

line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(HANDLER)

# 用于存储用户状态的字典
user_state = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    if user_id not in user_state:
        # 第一次与Bot互动，发送欢迎消息和选单
        welcome_message = TextSendMessage(text="您好，我是電影推薦小助手。")
        flex_message = FlexSendMessage(
            alt_text="電影選擇",
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://www.simplyrecipes.com/thmb/fUv6VKM4_ofF1s6oFP6LpdWsQzQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/Simply-Recipes-Perfect-Popcorn-LEAD-31-3af0091610534688987ea45b0efa472a.JPG",
                    "size": "full",
                    "aspect_ratio": "20:13",
                    "aspect_mode": "cover",
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "電影類型選擇",
                                "text": "電影類型選擇"
                            },
                            "style": "primary",
                            "color": "#00C300"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "自行輸入",
                                "text": "自行輸入"
                            },
                            "margin": "md"
                        }
                    ]
                }
            }
        )

        # 发送欢迎消息
        line_bot_api.reply_message(event.reply_token, welcome_message)

        # 设置用户状态为已发送欢迎消息
        user_state[user_id] = 'welcome_sent'

        # 发送Flex Message 选单
        line_bot_api.push_message(user_id, flex_message)

    else:
        # 已发送过欢迎消息和选单
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇一個選項。"))

if __name__ == "__main__":
    app.run(port=8000)
