from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import os

app = Flask(__name__)

# Environment variables on Render
LINE_BOT_API = os.environ.get('CHANNEL_ACCESS_TOKEN')  # Channel Access Token
HANDLER = os.environ.get('CHANNEL_SECRET')  # Channel Secret

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
    if event.message.text == "電影類型選擇":
        flex_message = FlexSendMessage(
            alt_text="電影類型選擇",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "請選擇電影類型",
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {"type": "button", "action": {"type": "message", "label": label, "text": label}}
                                for label in ["全部", "喜劇", "犯罪", "戰爭", "歌舞", "動畫", "驚悚", "懸疑", "恐怖",
                                              "科幻", "劇情", "冒險", "動作", "浪漫", "奇幻", "兒童", "默劇", "歷史",
                                              "短片", "傳記", "音樂", "家庭", "成人", "脫口秀", "實境秀"]
                            ]
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    elif event.message.text == "自行輸入":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您喜歡的電影類型，我會為您推薦相關電影。"))
    else:
        # 這裡可以根據用戶輸入的電影類型進行推薦，這部分可根據實際需求增加推薦邏輯
        recommendation = f"為您推薦一些{event.message.text}類型的電影：\n1. 示例電影A\n2. 示例電影B\n3. 示例電影C"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=recommendation))

if __name__ == "__main__":
    app.run(port=8000)

   
#     def Message_Postback(self, event):
#         if event.postback.data == 'action=0':
#             self.status = 0
#             message = self.Menu(None, 0)
#         elif event.postback.data == 'action=1-1':
#             message = self.Get_New(1)
#         elif event.postback.data == 'action=1-2':
#             message = self.Get_New(2)
#         elif event.postback.data == 'action=2-1':
#             self.status = 2
#             message = TextSendMessage(text='請輸入欲查詢的電影名稱(英文)')
#         elif event.postback.data == 'action=2-2': # 關鍵字搜尋附帶頁: 顯示更多
#             message = self.Keyword_Search(2)
#         elif event.postback.data == 'action=2-3': # 關鍵字搜尋失敗, self.status歸零
#             self.status = 0
#             message = TextSendMessage(text='關鍵字搜尋結束')
#         elif event.postback.data[0:10] == 'action=3-1':
#             text = event.postback.data.split('\n')[1:]
#             self.Update_Searched(text[0])
#             message = self.Get_Similar(text[1:], 1)
#         elif event.postback.data == 'action=3-2':
#             message = self.Get_Similar(None, 2)
#         elif event.postback.data == 'action=3-3':
#             message = self.Get_Similar(None, 3)
#         elif event.postback.data == 'action=4-1':
#             message = self.Read_Personal_Record()
#         elif event.postback.data[0:10] == 'action=5-1':
#             self.status = 5
#             self.scoring = event.postback.data.split('\n')[1:]
#             message = TextSendMessage(text='請輸入分數(1~10)')
#         elif event.postback.data == 'action=6-1':
#             message = self.Get_Recommended(get_more=False)
#         elif event.postback.data == 'action=6-2':
#             message = self.Get_Recommended(get_more=True)
#         else:
#             message = self.Menu(None, 0)
#         self.reset_gpt_log()
#         return message

# #第二選單
#     def Menu(self, keyword, home):
#         print("######### Menu ########")
#         if home == 0:
#             msg = TemplateSendMessage(
#                 alt_text='Buttons template',
#                 template=ButtonsTemplate(
#                     actions=[
#                         PostbackTemplateAction(
#                             label='全部',
#                             data='action=1-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='喜劇',
#                             data='action=2-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='犯罪',
#                             data='action=6-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='戰爭',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='歌舞',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='動畫',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='驚悚',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='恐怖',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='懸疑',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='科幻',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='劇情',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='冒險',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='動作',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='浪漫',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='奇幻',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='兒童',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='默劇',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='歷史',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='運動',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='短片',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='音樂',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='傳記',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='家庭',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='成人',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='家庭',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='實鏡秀',
#                             data='action=4-1'
#                         ),
#                         PostbackTemplateAction(
#                             label='脫口秀',
#                             data='action=4-1'
#                         )
#                     ]
#                 )
#             )


#         elif home == 1:
#             msg = CarouselColumn(
#                 thumbnail_image_url=honmpage_picture,
#                 title='最新電影',
#                 text='請選擇欲執行的功能',
#                 actions=[
#                     PostbackTemplateAction(
#                         label='顯示更多',
#                         data='action=1-2'
#                     ),
#                     PostbackTemplateAction(
#                         label='返回首頁',
#                         data='action=0'
#                     ),
#                     PostbackTemplateAction(
#                         label=' ',
#                         data='action=0'
#                     )
#                 ]
#             )
#         elif home == 2:
#             head = '\"'+keyword+'\"的搜尋結果' if keyword != None else '其他結果'
#             msg = CarouselColumn(
#                 thumbnail_image_url=honmpage_picture,
#                 title=head,
#                 text='請選擇欲執行的功能',
#                 actions=[
#                     PostbackTemplateAction(
#                         label='顯示更多',
#                         data='action=2-2'
#                     ),
#                     PostbackTemplateAction(
#                         label='重新搜尋',
#                         data='action=2-1'
#                     ),
#                     PostbackTemplateAction(
#                         label='返回首頁',
#                         data='action=0'
#                     )
#                 ]
#             )
#         elif home == 3:
#             msg = CarouselColumn(
#                 thumbnail_image_url=honmpage_picture,
#                 title='\"'+keyword+'\"的搜尋結果',

#                     )
#                 ]
#             )
#         elif home == 4:
#             msg = CarouselColumn(
#                 thumbnail_image_url=honmpage_picture,
#                 title='智慧推薦',
#                 text='請選擇欲執行的功能',
#                 actions=[
