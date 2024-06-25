from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent

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

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id

    # 发送欢迎消息和选单
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="您好，我是電影推薦小助手。"),
            FlexSendMessage(
                alt_text="電影選擇",
                contents={
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://miro.medium.com/v2/resize:fit:1100/format:webp/0*T3hzZYnWBEOrQzM1.jpg",
                        "size": "full",
                        "aspectRatio": "18:10",
                        "aspectMode": "cover",
                        "action": {
                            "type": "uri",
                            "uri": "https://line.me/"
                        }
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "md",
                                "action": {
                                    "type": "message",
                                    "label": "電影類型選擇",
                                    "text": "電影類型選擇"
                                }
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "md",
                                "action": {
                                    "type": "uri",
                                    "label": "自行輸入",
                                    "uri": "https://line.me/"
                                }
                            }
                        ],
                        "flex": 0
                    }
                }
            )
        ]
    )
    
    # 设置用户状态为已发送欢迎消息和选单
    user_state[user_id] = 'menu_sent'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    if text == "電影類型選擇":
        # 用户选择了電影類型選擇，发送电影类型选单
        movie_types = ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                       "科幻", "劇情", "冒險", "動作", "浪漫", "奇幻", "兒童", "默劇", "歷史",
                       "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]

        # 构建按钮，style交替设置
        buttons = [
            {
                "type": "button",
                "style": "link",
                "height": "md",
                "action": {
                    "type": "message",
                    "label": label,
                    "text": label
                }
            }
            for i, label in enumerate(movie_types)
        ]

        # 将按钮分成每行4个的布局
        rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]
        contents = [{"type": "box", "layout": "horizontal", "contents": row} for row in rows]

        # 调整最后一行的内容
        if len(rows[-1]) < 4:
            # 添加剩余的空白按钮使得每行都有4个按钮
            rows[-1].extend([
                {"type": "button", "style": "link", "height": "md", "action": {"type": "message", "label": " ", "text": " "}}
                for _ in range(4 - len(rows[-1]))
            ])

        # 更新最后一行的标签为要求的内容
        rows[-2][-1]["action"]["label"] = "音樂"
        rows[-2][-1]["action"]["text"] = "音樂"
        rows[-2][-2]["action"]["label"] = "家庭"
        rows[-2][-2]["action"]["text"] = "家庭"
        rows[-2][-3]["action"]["label"] = "成人"
        rows[-2][-3]["action"]["text"] = "成人"

        rows[-1][0]["action"]["label"] = "脫口秀"
        rows[-1][0]["action"]["text"] = "脫口秀"
        rows[-1][1]["action"]["label"] = "實境秀"
        rows[-1][1]["action"]["text"] = "實境秀"

        flex_message = FlexSendMessage(
            alt_text="電影類型選擇",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": contents
                }
            }
        )

        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        # 其他消息处理
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇一個選項。"))

if __name__ == "__main__":
    app.run(port=8000)
