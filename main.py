from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

app = Flask(__name__)

# LINE bot的Channel Access Token和Channel Secret
LINE_BOT_API = '1PAiU+EnukB7WtoP+lZEZR1diJ7YfpnNJbvno/WW1PwdhBHeHtDAtzaN1hgGEp5YkQHXGMRaeeahCS6Nr1LTvqfRRheTlPdSs/NXRDxqSYFxihhg8nFzV9FRhTnx+cgG/RxWHLBfuxpsERqyOfDQ4wdB04t89/1O/w1cDnyilFU='
HANDLER = ''910973d1cee8b1ee4407254e3ca5fb2d''

line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(HANDLER)

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
    if event.message.text == "電影":
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
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇一個選項。"))

if __name__ == "__main__":
    app.run(port=8000)
