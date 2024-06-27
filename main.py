import pandas as pd
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent
from linebot.models import ImageSendMessage

app = Flask(__name__)

# LINE bot的Channel Access Token和Channel Secret
LINE_BOT_API = '1PAiU+EnukB7WtoP+lZEZR1diJ7YfpnNJbvno/WW1PwdhBHeHtDAtzaN1hgGEp5YkQHXGMRaeeahCS6Nr1LTvqfRRheTlPdSs/NXRDxqSYFxihhg8nFzV9FRhTnx+cgG/RxWHLBfuxpsERqyOfDQ4wdB04t89/1O/w1cDnyilFU='
HANDLER = '910973d1cee8b1ee4407254e3ca5fb2d'

line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(HANDLER)

# 用于存储用户状态的字典
user_state = {}

# 读取CSV文件到一个全局变量
try:
    movies_df = pd.read_csv('movies.csv')
except pd.errors.EmptyDataError:
    movies_df = pd.DataFrame(columns=['title', 'year', 'genres', 'box_office', 'rate', 'country', 'picture'])

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
    text = event.message.text

    if text == "電影類型選擇":
        user_state[user_id] = {'menu': 'genre_selection'}

        genres = ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                  "科幻", "劇情", "冒險", "Action", "浪漫", "奇幻", "兒童", "默劇", "歷史",
                  "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]

        buttons = [
            {
                "type": "button",
                "style": "link",
                "height": "md",
                "action": {
                    "type": "message",
                    "label": genre,
                    "text": genre
                }
            }
            for genre in genres
        ]

        flex_message = FlexSendMessage(
            alt_text="電影類型選擇",
            contents={
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": buttons[:5]  # 只顯示前五個類型，可根據需要調整
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": buttons[5:10]  # 接著的五個類型
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": buttons[10:15]  # 再接著的五個類型
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": buttons[15:]  # 剩下的類型
                                }
                            ]
                        }
                    }
                ]
            }
        )

        line_bot_api.reply_message(event.reply_token, flex_message)

    elif text in ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                  "科幻", "劇情", "冒險", "Action", "浪漫", "奇幻", "兒童", "默劇", "歷史",
                  "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]:
        if user_id in user_state and user_state[user_id].get('menu') == 'genre_selection':
            user_state[user_id]['genre'] = text

            regions = ["全部", "亞洲", "歐洲", "英國", "非洲", "United States"]

            rows = [[
                {
                    "type": "button",
                    "style": "link",
                    "height": "md",
                    "action": {
                        "type": "message",
                        "label": region,
                        "text": region
                    }
                }
                for region in regions[i:i + 3]
            ] for i in range(0, len(regions), 3)]

            flex_message = FlexSendMessage(
                alt_text="地區選擇",
                contents={
                    "type": "carousel",
                    "contents": [
                        {
                            "type": "bubble",
                            "body": {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [{"type": "box", "layout": "horizontal", "contents": row} for row in rows]
                            }
                        }
                    ]
                }
            )

            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先選擇電影類型。"))

    elif text in ["全部", "亞洲", "歐洲", "英國", "非洲", "United States"]:
        if user_id in user_state and 'genre' in user_state[user_id]:
            user_state[user_id]['region'] = text

            selected_genre = user_state[user_id]['genre']
            selected_region = user_state[user_id]['region']

            # 根據用戶選擇的類型和地區篩選電影
            filtered_movies = movies_df[
                (movies_df['genres'].str.contains(selected_genre, case=False, na=False) | (selected_genre == "全部")) &
                (movies_df['country'].str.contains(selected_region, case=False, na=False) | (selected_region == "全部"))
            ]
            
            if not filtered_movies.empty:
                # 最多3部電影
                movies_list = filtered_movies.sample(min(3, len(filtered_movies)))

                bubbles = []
                for _, movie in movies_list.iterrows():
                    bubble = {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": movie['picture'],
                            "size": "full",
                            "aspectMode": "cover",
                            "aspectRatio": "320:213"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": movie['title'],
                                    "weight": "bold",
                                    "size": "sm",
                                    "wrap": True
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "contents": [
                                        {
                                            "type": "icon",
                                            "size": "xs",
                                            "url": "https://developers.line.biz/assets/images/app-icons/messaging-api.png"
                                        },
                                        {
                                            "type": "icon",
                                            "size": "xs",
                                            "url": "https://developers.line.biz/assets/images/app-icons/messaging-api.png"
                                        },
                                        {
                                            "type": "icon",
                                            "size": "xs",
                                            "url": "https://developers.line.biz/assets/images/app-icons/messaging-api.png"
                                        },
                                        {
                                            "type": "icon",
                                            "size": "xs",
                                            "url": "https://developers.line.biz/assets/images/app-icons/messaging-api.png"
                                        },
                                        {
                                            "type": "icon",
                                            "size": "xs",
                                            "url": "https://developers.line.biz/assets/images/app-icons/messaging-api.png"
                                        },
                                        {
                                            "type": "text",
                                            "text": "4.7",
                                            "size": "xs",
                                            "color": "#8c8c8c",
                                            "margin": "md",
                                            "flex": 0
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": movie['year'] + "年",
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5
                                        },
                                        {
                                            "type": "text",
                                            "text": movie['country'],
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5
                                        },
                                        {
                                            "type": "text",
                                            "text": "票房",
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5
                                        },
                                        {
                                            "type": "text",
                                            "text": movie['box_office'],
                                            "wrap": True,
                                            "color": "#8c8c8c",
                                            "size": "xs",
                                            "flex": 5
                                        }
                                    ]
                                }
                            ],
                            "spacing": "sm",
                            "paddingAll": "13px"
                        }
                    }
                    bubbles.append(bubble)

                carousel_message = FlexSendMessage(
                    alt_text="電影推薦",
                    contents={
                        "type": "carousel",
                        "contents": bubbles
                    }
                )

                line_bot_api.reply_message(event.reply_token, carousel_message)
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="沒有符合條件的電影。"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先選擇電影類型。"))

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇一個選項。"))

if __name__ == "__main__":
    app.run(port=8000)

# import pandas as pd
# import random
# from flask import Flask, request, abort
# from linebot import LineBotApi, WebhookHandler
# from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent

# app = Flask(__name__)

# # LINE bot的Channel Access Token和Channel Secret
# LINE_BOT_API = '1PAiU+EnukB7WtoP+lZEZR1diJ7YfpnNJbvno/WW1PwdhBHeHtDAtzaN1hgGEp5YkQHXGMRaeeahCS6Nr1LTvqfRRheTlPdSs/NXRDxqSYFxihhg8nFzV9FRhTnx+cgG/RxWHLBfuxpsERqyOfDQ4wdB04t89/1O/w1cDnyilFU='
# HANDLER = '910973d1cee8b1ee4407254e3ca5fb2d'

# line_bot_api = LineBotApi(LINE_BOT_API)
# handler = WebhookHandler(HANDLER)

# # 用于存储用户状态的字典
# user_state = {}

# # 读取CSV文件到一个全局变量
# try:
#     movies_df = pd.read_csv('action.csv')
# except pd.errors.EmptyDataError:
#     movies_df = pd.DataFrame(columns=['title', 'rate', 'information', 'country', 'box_office'])

# @app.route("/callback", methods=['POST'])
# def callback():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)

#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     return 'OK'

# @handler.add(FollowEvent)
# def handle_follow(event):
#     user_id = event.source.user_id

#     # 发送欢迎消息和选单
#     line_bot_api.reply_message(
#         event.reply_token,
#         [
#             TextSendMessage(text="您好，我是電影推薦小助手。"),
#             FlexSendMessage(
#                 alt_text="電影選擇",
#                 contents={
#                     "type": "bubble",
#                     "hero": {
#                         "type": "image",
#                         "url": "https://miro.medium.com/v2/resize:fit:1100/format:webp/0*T3hzZYnWBEOrQzM1.jpg",
#                         "size": "full",
#                         "aspectRatio": "18:10",
#                         "aspectMode": "cover",
#                         "action": {
#                             "type": "uri",
#                             "uri": "https://line.me/"
#                         }
#                     },
#                     "footer": {
#                         "type": "box",
#                         "layout": "vertical",
#                         "spacing": "sm",
#                         "contents": [
#                             {
#                                 "type": "button",
#                                 "style": "primary",
#                                 "height": "md",
#                                 "action": {
#                                     "type": "message",
#                                     "label": "電影類型選擇",
#                                     "text": "電影類型選擇"
#                                 }
#                             },
#                             {
#                                 "type": "button",
#                                 "style": "secondary",
#                                 "height": "md",
#                                 "action": {
#                                     "type": "uri",
#                                     "label": "自行輸入",
#                                     "uri": "https://line.me/"
#                                 }
#                             }
#                         ],
#                         "flex": 0
#                     }
#                 }
#             )
#         ]
#     )
    
#     user_state[user_id] = 'menu_sent'

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_id = event.source.user_id
#     text = event.message.text

#     if text == "電影類型選擇":
#         movie_types = ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
#                        "科幻", "劇情", "冒險", "Action", "浪漫", "奇幻", "兒童", "默劇", "歷史",
#                        "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]

#         buttons = [
#             {
#                 "type": "button",
#                 "style": "link",
#                 "height": "md",
#                 "action": {
#                     "type": "message",
#                     "label": label,
#                     "text": label
#                 }
#             }
#             for label in movie_types
#         ]

#         rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]

#         if len(rows[-1]) < 4:
#             rows[-1].extend([
#                 {"type": "button", "style": "link", "height": "md", "action": {"type": "message", "label": " ", "text": " "}}
#                 for _ in range(4 - len(rows[-1]))
#             ])

#         flex_message = FlexSendMessage(
#             alt_text="電影類型選擇",
#             contents={
#                 "type": "bubble",
#                 "body": {
#                     "type": "box",
#                     "layout": "vertical",
#                     "spacing": "sm",
#                     "contents": [{"type": "box", "layout": "horizontal", "contents": row} for row in rows]
#                 }
#             }
#         )

#         line_bot_api.reply_message(event.reply_token, flex_message)

#     elif text in ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
#                   "科幻", "劇情", "冒險", "Action", "浪漫", "奇幻", "兒童", "默劇", "歷史",
#                   "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]:
#         user_state[user_id] = {'genre': text}

#         regions = ["全部", "亞洲", "歐洲", "英國", "非洲", "United States"]

#         rows = [[
#             {
#                 "type": "button",
#                 "style": "link",
#                 "height": "md",
#                 "action": {
#                     "type": "message",
#                     "label": region,
#                     "text": region
#                 }
#             }
#             for region in regions[i:i + 3]
#         ] for i in range(0, len(regions), 3)]

#         flex_message = FlexSendMessage(
#             alt_text="地區選擇",
#             contents={
#                 "type": "bubble",
#                 "body": {
#                     "type": "box",
#                     "layout": "vertical",
#                     "spacing": "sm",
#                     "contents": [{"type": "box", "layout": "horizontal", "contents": row} for row in rows]
#                 }
#             }
#         )

#         line_bot_api.reply_message(event.reply_token, flex_message)

#     elif text in ["全部", "亞洲", "歐洲", "英國", "非洲", "United States"]:
#         if user_id in user_state and 'genre' in user_state[user_id]:
#             user_state[user_id]['region'] = text

#             # 从CSV文件中随机选择3部电影
#             if not movies_df.empty:
#                 random_movies = movies_df.sample(min(3, len(movies_df)))

#                 movie_messages = []
#                 for _, movie in random_movies.iterrows():
#                     movie_message = (
#                         f"片名: {movie['title']}\n"
#                         f"評分: {movie['rate']}\n"
#                         f"簡介: {movie['information']}\n"
#                         f"地區: {movie['country']}\n"
#                         f"票房：{movie['box_office']}"
#                     )
#                     movie_messages.append(TextSendMessage(text=movie_message))

#                 line_bot_api.reply_message(event.reply_token, movie_messages)
#             else:
#                 line_bot_api.reply_message(event.reply_token, TextSendMessage(text="沒有符合條件的電影。"))
#         else:
#             line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先選擇電影類型。"))
#     else:
#         line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇一個選項。"))

# if __name__ == "__main__":
#     app.run(port=8000)
