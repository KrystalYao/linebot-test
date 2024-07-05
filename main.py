import os
import random
import pandas as pd
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, FollowEvent,
    BubbleContainer, BoxComponent, ButtonComponent, CarouselContainer, ImageComponent,
    MessageAction, TextComponent, IconComponent
)
from openai import OpenAI
import traceback

app = Flask(__name__)

# 使用环境变量存储敏感信息
LINE_BOT_API = '1PAiU+EnukB7WtoP+lZEZR1diJ7YfpnNJbvno/WW1PwdhBHeHtDAtzaN1hgGEp5YkQHXGMRaeeahCS6Nr1LTvqfRRheTlPdSs/NXRDxqSYFxihhg8nFzV9FRhTnx+cgG/RxWHLBfuxpsERqyOfDQ4wdB04t89/1O/w1cDnyilFU='
HANDLER = '910973d1cee8b1ee4407254e3ca5fb2d'
OPENAI_API_KEY = os.getenv('sk-proj-9HKvRp7S3pqAuLr0jvzUT3BlbkFJZG5zeVj3lKW8XRev7Xx1')

line_bot_api = LineBotApi(LINE_BOT_API)
handler = WebhookHandler(HANDLER)

client = OpenAI(api_key=OPENAI_API_KEY)

# 用于存储用户状态的字典
user_state = {}

# 读取CSV文件到一个全局变量
try:
    movies_df = pd.read_csv('movies.csv')
except pd.errors.EmptyDataError:
    movies_df = pd.DataFrame(columns=['title', 'year', 'genres', 'rate', 'country', 'picture', 'summary'])

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

def send_welcome_message(reply_token):
    line_bot_api.reply_message(
        reply_token,
        [
            TextSendMessage(text="您好，我是電影推薦小助手。"),
            FlexSendMessage(
                alt_text="電影選擇",
                contents=BubbleContainer(
                    hero=ImageComponent(
                        url="https://miro.medium.com/v2/resize:fit:1100/format:webp/0*T3hzZYnWBEOrQzM1.jpg",
                        size="full",
                        aspect_ratio="18:10",
                        aspect_mode="cover",
                        action=MessageAction(label="請複製以下訊息至對話框，並輸入想查詢的電影\n\n電影名稱：\n綜合評分：\n票房：\n年份：\n國家：\n類型：\n簡介：\n網友評價(2則)：", text="請複製以下訊息至對話框，並輸入想查詢的電影\n\n電影名稱：\n綜合評分：\n票房：\n年份：\n國家：\n類型：\n簡介：\n網友評價(2則)：")
                    ),
                    footer=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        contents=[
                            ButtonComponent(
                                style="primary",
                                height="md",
                                action=MessageAction(label="電影類型選擇", text="電影類型選擇")
                            ),
                            ButtonComponent(
                                style="secondary",
                                height="md",
                                action=MessageAction(label="自行輸入", text="請複製以下訊息至對話框，並輸入想查詢的電影\n\n電影名稱：\n綜合評分：\n票房：\n年份：\n國家：\n類型：\n簡介：\n網友評價(2則)：") 
                            )
                        ],
                        flex=0
                    )
                )
            )
        ]
    )
    user_state[user_id] = 'menu_sent'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    try:
        if text == "請複製以下訊息至對話框，並輸入想查詢的電影\n\n電影名稱：\n綜合評分：\n票房：\n年份：\n國家：\n類型：\n簡介：\n網友評價(2則)：":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請複製以下訊息至對話框，並輸入想查詢的電影\n\n電影名稱：\n綜合評分：\n票房：\n年份：\n國家：\n類型：\n簡介：\n網友評價(2則)：")
            )
        elif text == "電影類型選擇":
            movie_types = ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                               "科幻", "冒險", "動作", "浪漫", "奇幻", "音樂", "家庭"]

            buttons = [
                ButtonComponent(
                    style="link",
                    height="md",
                    action=MessageAction(label=label, text=label)
                ) for label in movie_types
            ]

            rows = [buttons[i:i + 4] for i in range(0, len(buttons), 4)]

            if len(rows[-1]) < 4:
                rows[-1].extend([
                    ButtonComponent(
                        style="link",
                        height="md",
                        action=MessageAction(label=" ", text=" ")
                    ) for _ in range(4 - len(rows[-1]))
                ])

            flex_message = FlexSendMessage(
                alt_text="電影類型選擇",
                contents=BubbleContainer(
                    body=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        contents=[BoxComponent(layout="horizontal", contents=row) for row in rows]
                    )
                )
            )
            
            line_bot_api.reply_message(event.reply_token, flex_message)
        
        elif text in ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                      "科幻", "冒險", "動作", "浪漫", "奇幻", "音樂", "家庭"]:
            user_state[user_id] = {'genre': text}

            regions = ["亞洲", "歐洲", "英國", "美國"]

            rows = [[
                ButtonComponent(
                    style="link",
                    height="md",
                    action=MessageAction(label=region, text=region)
                ) for region in regions[i:i + 4]
            ] for i in range(0, len(regions), 4)]

            flex_message = FlexSendMessage(
                alt_text="地區選擇",
                contents=BubbleContainer(
                    body=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        contents=[BoxComponent(layout="horizontal", contents=row) for row in rows]
                    )
                )
            )
            line_bot_api.reply_message(event.reply_token, flex_message)

        elif text in ["亞洲", "歐洲", "英國", "美國"]:
            if user_id in user_state and 'genre' in user_state[user_id]:
                user_state[user_id]['region'] = text

                selected_genre = user_state[user_id]['genre']
                selected_region = user_state[user_id]['region']

                if selected_genre == "全部":
                    selected_genre = ""

                if selected_region == "歐洲":
                    europe_countries = [
                        "奧地利", "比利時", "保加利亞", "克羅埃西亞", "賽普勒斯", "捷克", "丹麥", "愛沙尼亞",
                        "芬蘭", "法國", "德國", "希臘", "匈牙利", "愛爾蘭", "義大利", "拉脫維亞", "立陶宛",
                        "盧森堡", "馬爾他", "荷蘭", "波蘭", "葡萄牙", "羅馬尼亞", "斯洛伐克", "斯洛維尼亞",
                        "西班牙", "瑞典"
                    ]

                    filtered_movies = movies_df[
                        (movies_df['genres'].str.contains(selected_genre, case=False, na=False)) &
                        (movies_df['country'].isin(europe_countries))
                    ]
                elif selected_region == "亞洲":
                    asian_countries = [
                        "中國大陸", "中國香港", "台灣", "日本", "韓國", "菲律賓", "印尼", "泰國",
                        "馬來西亞", "新加坡", "越南", "柬埔寨", "緬甸", "汶萊"
                    ]

                    filtered_movies = movies_df[
                        (movies_df['genres'].str.contains(selected_genre, case=False, na=False)) &
                        (movies_df['country'].isin(asian_countries))
                    ]
                else:
                    filtered_movies = movies_df[
                        (movies_df['genres'].str.contains(selected_genre, case=False, na=False)) &
                        (movies_df['country'].str.contains(selected_region, case=False, na=False))
                    ]

                if not filtered_movies.empty:
                    random_movies = filtered_movies.sample(min(3, len(filtered_movies)))
                    movie_messages = []
                    for _, movie in random_movies.iterrows():
                        # Randomly select two comments
                        comments = random.sample([movie['comment1'], movie['comment2'], movie['comment3'], movie['comment4'], movie['comment5']], 2)
                        comments_text = "\n\n".join([f"Comment {i+1}: {comment}" for i, comment in enumerate(comments)])
                    
                        movie_message = BubbleContainer(
                            size="mega",
                            hero=ImageComponent(
                                url=movie['picture'],
                                size="full",
                                aspect_ratio="16:9",
                                aspect_mode="cover"
                            ),
                            body=BoxComponent(
                                layout="vertical",
                                spacing="sm",
                                contents=[
                                    TextComponent(
                                        text=movie['title'],
                                        weight="bold",
                                        size="xl",
                                        wrap=True
                                    ),
                                    BoxComponent(
                                        layout="baseline",
                                        margin="md",
                                        contents=[
                                            IconComponent(
                                                size="sm",
                                                url="https://developers.line.biz/fx/review_gold_star_28.png"
                                            ),
                                            TextComponent(
                                                text=f" {str(movie['rate'])}",
                                                size="sm",
                                                color="#999999",
                                                margin="md"
                                            )
                                        ]
                                    ),
                                    TextComponent(
                                        text=f"{str(movie['year']).replace('.0', '年')} | {movie['country']}",
                                        size="sm",
                                        color="#999999",
                                        wrap=True
                                    ),
                                    TextComponent(
                                        text=movie['genres'],
                                        size="sm",
                                        color="#999999",
                                        wrap=True
                                    ),
                                    TextComponent(
                                        text=movie['summary'],
                                        size="sm",
                                        color="#999999",
                                        wrap=True
                                    ),
                                    ButtonComponent(
                                        style="link",
                                        height="sm",
                                        action=MessageAction(
                                            label="查看評論",
                                            text=f"{movie['title']}\n\n{comments_text}"
                                        )
                                    )
                                ]
                            )
                        )
                        movie_messages.append(movie_message)
                    
                    line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="電影推薦", contents=CarouselContainer(contents=movie_messages)))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到符合條件的電影。"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先選擇電影類型。"))

        else:
            # If none of the above conditions are met, send the initial movie selection menu
            line_bot_api.reply_message(
                event.reply_token,
                [
                    FlexSendMessage(
                        alt_text="電影選擇",
                        contents=BubbleContainer(
                            hero=ImageComponent(
                                url="https://miro.medium.com/v2/resize:fit:1100/format:webp/0*T3hzZYnWBEOrQzM1.jpg",
                                size="full",
                                aspect_ratio="18:10",
                                aspect_mode="cover",
                                action=MessageAction(label="請輸入想查詢的電影名稱", text="請輸入想查詢的電影名稱")
                            ),
                            footer=BoxComponent(
                                layout="vertical",
                                spacing="sm",
                                contents=[
                                    ButtonComponent(
                                        style="primary",
                                        height="md",
                                        action=MessageAction(label="電影類型選擇", text="電影類型選擇")
                                    ),
                                    ButtonComponent(
                                        style="secondary",
                                        height="md",
                                        action=MessageAction(label="自行輸入", text="請輸入想查詢的電影名稱")
                                    )
                                ],
                                flex=0
                            )
                        )
                    )
                ]
            )

    except Exception as e:
        print(traceback.format_exc())
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="發生了一些問題，請稍後再試。")
        )

def ask_openai(input_text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    app.run()

