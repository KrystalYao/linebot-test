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
    send_welcome_message(event.reply_token)
    user_state[user_id] = 'menu_sent'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    try:
        if text == "請輸入想查詢的電影名稱":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入想查詢的電影名稱")
            )
        elif text == "電影類型選擇":
            send_movie_type_selection(event.reply_token)
        elif text in ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                      "科幻", "冒險", "動作", "浪漫", "奇幻", "音樂", "家庭"]:
            user_state[user_id] = {'genre': text}
            send_region_selection(event.reply_token)
        elif text in ["亞洲", "歐洲", "英國", "美國"]:
            handle_region_selection(user_id, text, event.reply_token)
        else:
            response = ask_openai(text)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response)
            )
    except Exception as e:
        print(traceback.format_exc())
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('發生了一些問題，請稍後再試。')
        )

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

def send_movie_type_selection(reply_token):
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

    line_bot_api.reply_message(reply_token, flex_message)

def send_region_selection(reply_token):
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
    line_bot_api.reply_message(reply_token, flex_message)

def handle_region_selection(user_id, selected_region, reply_token):
    if user_id in user_state and 'genre' in user_state[user_id]:
        user_state[user_id]['region'] = selected_region

        selected_genre = user_state[user_id]['genre']

        if selected_genre == "全部":
            selected_genre = ""

        filtered_movies = filter_movies(selected_genre, selected_region)

        if not filtered_movies.empty:
            random_movies = filtered_movies.sample(min(3, len(filtered_movies)))
            movie_messages = [create_movie_message(movie) for _, movie in random_movies.iterrows()]
            line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="電影推薦", contents=CarouselContainer(contents=movie_messages)))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="沒有符合條件的電影。"))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請先選擇電影類型。"))

def filter_movies(genre, region):
    if region == "歐洲":
        europe_countries = [
            "奧地利", "比利時", "保加利亞", "克羅埃西亞", "賽普勒斯", "捷克", "丹麥", "愛沙尼亞",
            "芬蘭", "法國", "德國", "希臘", "匈牙利", "愛爾蘭", "義大利", "拉脫維亞", "立陶宛",
            "盧森堡", "馬爾他", "荷蘭", "波蘭", "葡萄牙", "羅馬尼亞", "斯洛伐克", "斯洛維尼亞",
            "西班牙", "瑞典"
        ]
        return movies_df[
            (movies_df['genres'].str.contains(genre, case=False, na=False)) &
            (movies_df['country'].isin(europe_countries))
        ]
    elif region == "亞洲":
        asian_countries = [
            "中國大陸", "中國香港", "台灣", "日本", "韓國", "菲律賓", "印尼", "泰國",
            "馬來西亞", "新加坡", "越南", "柬埔寨", "緬甸", "汶萊"
        ]
        return movies_df[
            (movies_df['genres'].str.contains(genre, case=False, na=False)) &
            (movies_df['country'].isin(asian_countries))
        ]
    else:
        return movies_df[
            (movies_df['genres'].str.contains(genre, case=False, na=False)) &
            (movies_df['country'].str.contains(region, case=False, na=False))
        ]

def create_movie_message(movie):
    comments = random.sample([movie['評論1'], movie['評論2'], movie['評論3'], movie['評論4'], movie['評論5']], 2)
    comments_text = "\n\n".join([f"評論{i+1}: {comment}" for i, comment in enumerate(comments)])
    
    return BubbleContainer(
        size="deca",
        hero=ImageComponent(
            url=movie['picture'],
            size="full",
            aspect_mode="cover",
            aspect_ratio="150:100"
        ),
        body=BoxComponent(
            layout="vertical",
            spacing="sm",
            contents=[
                TextComponent(
                    text=movie['title'],
                    weight="bold",
                    size="md",
                    wrap=True
                ),
                BoxComponent(
                    layout="baseline",
                    contents=[
                        IconComponent(
                            size="sm",
                            url="https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        ),
                        TextComponent(
                            text=f" {str(movie['rate'])}",
                            size="md",
                            color="#8c8c8c",
                            flex=0
                        )
                    ]
                ),
                BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(
                            text=str(movie['year']).replace('.0', '年'),
                            wrap=True,
                            color="#8c8c8c",
                            size="md",
                            flex=5
                        ),
                        TextComponent(
                            text=movie['country'],
                            wrap=True,
                            color="#8c8c8c",
                            size="md",
                            flex=5,
                            margin="5px"
                        ),
                        TextComponent(
                            text=movie['genres'],
                            wrap=True,
                            color="#8c8c8c",
                            size="md",
                            flex=5,
                            margin="5px"
                        ),
                        TextComponent(
                            text=movie['summary'],
                            wrap=True,
                            color="#8c8c8c",
                            size="sm",
                            flex=5,
                            margin="5px"
                        ),
                        ButtonComponent(
                            style="link",
                            text="點選可查看網友評論",
                            height="sm",
                            color="#2828FF",
                            size="xs",
                            align="end",
                            decoration="underline",
                            action=MessageAction(
                                label="點選可查看網友評論",
                                text=f"{movie['title']}\n\n{comments_text}"
                            )
                        )
                    ]
                )
            ]
        ),
        padding_all="13px"
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
