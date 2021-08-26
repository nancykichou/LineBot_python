# -*- coding: utf-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import re
from linebot.models.responses import Profile
from database import db_session, init_db  # 資料系結
from user import Users  # 資料系結 class Users
from product import Products  # 資料系結 class Products
from cart import Cart  # 資料系結 class Cart
from urllib.parse import quote  # 避免使用者 按到空白建
from config import Config
from order import Orders
from item import Items

# payment
from linepay import LinePay
from urllib.parse import parse_qsl
import uuid

app = Flask(__name__)


line_bot_api = LineBotApi(Config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.CHANNEL_SECRET)
line_bot_api.push_message(
    Config.DEVELOPER_USER_ID, TextSendMessage(text='歡迎來到 悠然美地~~'))
##################function########################################################


#歡迎訊息
def Usage(event):
    push_msg(event, {
        "type": "bubble",
        "hero": {
    "type": "image",
    "url": "https://i.imgur.com/uLMLThz.jpg",
    "size": "250px",
    "aspectMode": "fit",
    "action": {
      "type": "uri",
      "uri": "http://linecorp.com/"
    },
    "aspectRatio": "1142:400"
  },
        "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "💪Covid-19防疫 也要忙裡偷閒☘",
        "size": "md",
        "margin": "none",
        "offsetBottom": "md"
      },
      {
        "type": "text",
        "text": "TLC保證✊ 隔間只為一位客人服務",
        "size": "md",
        "margin": "none"
      },
      {
        "type": "text",
        "text": "服務完上個客人 間隔1小時徹底消毒",
        "size": "md",
        "margin": "none"
      },
      {
        "type": "text",
        "text": "以保證防疫安全 人客安心💜",
        "size": "md",
        "margin": "none",
        "offsetBottom": "none",
        "offsetStart": "none"
      }
    ]
  },
        "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "FaceBook",
          "uri": "https://www.facebook.com/TLCBeautyProducts"
        },
        "style": "primary",
        "color": "#3741b4",
        "height": "md",
        "margin": "md"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "Pinterest",
          "uri": "http://linecorp.com/"
        },
        "style": "primary",
        "margin": "md",
        "color": "#b92121"
      }
    ]
  }
        }
    )

def push_msg(event, msg):
    try:
        user_id = event.source.user_id
        line_bot_api.push_message(user_id, FlexSendMessage(alt_text='welcome', contents=msg))
    except:
        room_id = event.source.room_id
        line_bot_api.push_message(room_id, FlexSendMessage(alt_text='welcome', contents=msg))


@app.teardown_appcontext  # 加上這個function可以幫助我們每一次抓完資料 就關掉資料庫鏈結
def shutdown_session(exception=None):
    db_session.remove()

# 建立 或 取得 user
def get_or_create_user(user_id):
    user = db_session.query(Users).filter_by(id=user_id).first()
    if not user:
        profile = line_bot_api.get_profile(user_id)
        user = Users(id=user_id, nick_name=profile.display_name,
                     image_url=profile.picture_url)
        db_session.add(user)
        db_session.commit()

#定義 Ascii英文的部分
def is_ascii(s):
    return all(ord(c) < 128 for c in s)


@app.route("/confirm")
def confirm():
    transaction_id = request.args.get('transactionId')
    order = db_session.query(Orders).filter(
        Orders.transaction_id == transaction_id).first()

    if order:
        line_pay = LinePay()
        line_pay.confirm(transaction_id=transaction_id, amount=order.amount)

        order.is_pay = True  # 確認收款無誤時就會改成已付款
        db_session.commit()

        # 傳收據給用戶
        message = order.display_receipt()
        line_bot_api.push_message(to=order.user_id, messages=message)

        return '<h1>已收到您的付款. 我們會盡快為您出貨 感謝!!</h1>'

# 主程式


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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_or_create_user(event.source.user_id)
    #message_text = str(event.message.text).lower()  # 將所有的字變成小寫
    emsg = event.message.text
    message = None
    #顯示中文
    if is_ascii(str(event.message.text)):
        message_text = str(event.message.text).lower()
    else:
        message_text = event.message.text

    ##### "測試" 取得使用者資訊 #########
    ##### 顯示於Heroku 專案' log #########
    '''print(event.source.user_id)
    profile = line_bot_api.get_profile(event.source.user_id)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.display_name)  # 使用者 狀態消息'''

    cart = Cart(user_id=event.source.user_id)
    #if re.match('/help', emsg):
        #Usage(event)
    if message_text in ["/help", "最新活動"]:
        bubbleAction = {
            "type": "carousel",
            "contents": [
    {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "https://i.imgur.com/xn2wbpQ.png",
        "aspectRatio": "20:13",
        "aspectMode": "cover",
        "size": "full"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "🌟放鬆著、美麗著🌟",
            "size": "md",
            "margin": "none",
            "offsetBottom": "sm",
            "weight": "bold"
          },
          {
            "type": "text",
            "text": "🍀臉部精細保養 [1800]"
          },
          {
            "type": "text",
            "text": "🍀忙裡偷閒基礎臉部保養 [1200]"
          },
          {
            "type": "text",
            "text": "🍀全身放鬆按摩保養 [2500]"
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "🤙台南--預約",
              "uri": "tel://0800888123"
            },
            "style": "primary",
            "color": "#e0214f"
          },
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "🤙台中--預約",
              "uri": "tel://0800888123"
            },
            "style": "secondary",
            "margin": "md",
            "color": "#f09ba0"
          }
        ]
      }
    },
    {
      "type": "bubble",
      "hero": {
        "type": "image",
        "url": "https://i.imgur.com/vXSwD0g.png",
        "aspectRatio": "20:13",
        "size": "full",
        "aspectMode": "cover"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "🌟夏日來了、美、自信展現🌟",
            "size": "md",
            "margin": "none",
            "offsetBottom": "sm",
            "weight": "bold"
          },
          {
            "type": "text",
            "text": "💜女性全身蜜糖除毛[2500]"
          },
          {
            "type": "text",
            "text": "💜男性全身蜜糖除毛[2800]"
          },
          {
            "type": "text",
            "text": "💜不再毛手毛腳[1888]"
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "🤙台南--預約",
              "uri": "tel://0800888123"
            },
            "style": "primary",
            "color": "#e0214f"
          },
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "🤙台中--預約",
              "uri": "tel://0800888123"
            },
            "style": "secondary",
            "margin": "md",
            "color": "#f09ba0"
          }
        ]
      }
    }
  ]
        }
        # line_bot_api.reply_message(
        #    event.reply_token,
        #    FlexSendMessage(alt_text="預約介面", contents=bubbles)
        # )
        message = FlexSendMessage(alt_text='new action', contents=bubbleAction)

    # 電話預約 顯示 ()
    elif message_text in ["reservation", "reservation"]:
        # message = [
        #     ImageSendMessage(
        #         original_content_url='https://i.imgur.com/DKzbk3l.jpg',
        #         preview_image_url='https://i.imgur.com/DKzbk3l.jpg'
        #     ), StickerSendMessage(
        #         # 熊大
        #         package_id='11537',
        #         sticker_id='52002734'
        #     )
        # ]
        bubbles = {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://i.imgur.com/Py6D6GC.jpg",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "size": "full"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "服務據點 - 台南",
                                "margin": "md",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": "營業時間",
                                "margin": "md",
                                "size": "md",
                                "weight": "bold",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": "星期一至五：12:30~21:00",
                                "size": "xs",
                                "margin": "none",
                                "color": "#AAAAAA",
                                "offsetTop": "sm"
                            },
                            {
                                "type": "text",
                                "text": "星期六：10:00~19:00",
                                "size": "xs",
                                "color": "#AAAAAA"
                            },
                            {
                                "type": "text",
                                "text": "星期日公休日",
                                "size": "xs",
                                "color": "#AAAAAA"
                            },
                            {
                                "type": "text",
                                "text": "701 台南市東豐路433號1樓",
                                "size": "sm",
                                "color": "#AAAAAA",
                                "weight": "bold",
                                "offsetTop": "lg"
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "預約電話",
                                    "uri": "tel://0988287583"
                                },
                                "style": "primary",
                                "color": "#f09ba0"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "地圖導覽 >",
                                    "uri": "https://goo.gl/maps/wYz2p6cRR4qqP4LD7"
                                },
                                "style": "link"
                            }
                        ]
                    }
                },
                {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://i.imgur.com/CnCU2ff.jpg",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "size": "full"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "服務據點 - 台中",
                                "margin": "md",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": "營業時間",
                                "margin": "md",
                                "size": "md",
                                "weight": "bold",
                                "color": "#555555"
                            },
                            {
                                "type": "text",
                                "text": "星期一至五：12:30~21:00",
                                "size": "xs",
                                "margin": "none",
                                "color": "#AAAAAA",
                                "offsetTop": "sm"
                            },
                            {
                                "type": "text",
                                "text": "星期六：10:00~19:00",
                                "size": "xs",
                                "color": "#AAAAAA"
                            },
                            {
                                "type": "text",
                                "text": "星期日公休日",
                                "size": "xs",
                                "color": "#AAAAAA"
                            },
                            {
                                "type": "text",
                                "text": "401 台中市東元路433號1樓",
                                "size": "sm",
                                "color": "#AAAAAA",
                                "weight": "bold",
                                "offsetTop": "lg"
                            }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "預約電話",
                                    "uri": "tel://0988287583"
                                },
                                "style": "primary",
                                "color": "#f09ba0"
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "uri",
                                    "label": "地圖導覽 >",
                                    "uri": "https://goo.gl/maps/wYz2p6cRR4qqP4LD7"
                                },
                                "style": "link"
                            }
                        ]
                    }
                }
            ]
        }
        # line_bot_api.reply_message(
        #    event.reply_token,
        #    FlexSendMessage(alt_text="預約介面", contents=bubbles)
        # )
        message = FlexSendMessage(alt_text='reservation', contents=bubbles)

    # list produst 顯示 ( from product import Products, method list_all in class Produsts)
    elif message_text in ['i am ready to order.', 'add']:
        message = Products.list_all()

    # elif message_text in ['my cart', "that's it."]:
        ##message = TextSendMessage(text='cart')

    # 加入購物車 Cart
    elif "想訂購數量" in message_text:
        product_name = message_text.split(',')[0]
        num_item = message_text.rsplit(':')[1]
        product = db_session.query(Products).filter(
            Products.name.ilike(product_name)).first()
        if product:
            cart.add(product=product_name, num=num_item)
            if cart.bucket():
                message = cart.display()
            else:
                message = TextSendMessage(text='購物車是空的 請擺些東西進去 😻')
            # confirm_template=ConfirmTemplate(
            #     text='Sure,{} {}, anything else?'.format(num_item,product_name),
            #     actions=[
            #         MessageAction(label='Add',text='add'),
            #         MessageAction(label="that's it.", text="that's it.")
            #     ])
            # message=TemplateSendMessage(alt_text="anythiny else?",template=confirm_template)

            # 設定 Flex message (in BubbleContainer)
            # bubble = BubbleContainer(
            #     direction='ltr',
            #     body=BoxComponent(
            #         layout='vertical',
            #         contents=[
            #             TextComponent(
            #                 text='將 {}X{}'.format(product_name, num_item), color='#6568ef', wrap=True, size='lg', margin='md', align='center'),
            #             TextComponent(
            #                 text='放入購物車, 要繼續加購嗎?', wrap=True, size='md', margin='md', align='center')
            #         ]
            #     ),
            #     footer=BoxComponent(  # 最底端的地方
            #         layout='vertical',
            #         spacing='md',
            #         contents=[
            #             ButtonComponent(
            #                 style='primary',
            #                 color='#f09ba0',
            #                 action=MessageAction(label='繼續購買',
            #                                      text='add')
            #             ),
            #             BoxComponent(
            #                 layout='horizontal',
            #                 spacing='md',
            #                 contents=[
            #                     ButtonComponent(
            #                         style='primary',
            #                         color='#cc9c9e',
            #                         height='sm',
            #                         flex=3,
            #                         action=MessageAction(label='清空購物車',
            #                                              text='Empty cart'),
            #                     ),
            #                     ButtonComponent(
            #                         style='primary',
            #                         color='#f09ba0',
            #                         height='sm',
            #                         flex=2,
            #                         action=MessageAction(label='不了、結帳',
            #                                              text="that's it."),
            #                     )
            #                 ]

            #             )
            #         ]
            #     )
            # )
            # flex message alt_text 文字顯示, contents 設定好的 flex message
            #message = FlexSendMessage(alt_text='Continue', contents=bubble)

        else:
            message = TemplateSendMessage(
                alt_text="不好意思 目前 {} 尚未上架.".format(product_name))
        print(cart.bucket())

    ## 顯示 (購物車)
    # 確認購物車內容 Cart
    elif message_text in ["my cart", "cart", "that's it."]:
        if cart.bucket():
            message = cart.display()
        else:
            message = TextSendMessage(text='購物車是空的 請擺些東西進去 😻')

    elif message_text == 'empty cart':
        cart.reset()
        message = TextSendMessage(text='您的購物車已清空，請您重新訂購 😻')

    if re.match("自動推播", emsg):
        import schedule
        import time  # 無窮迴圈

        def job():
            print('testing...')
            Usage(event)

        schedule.every(30).seconds.do(job)  # 每30秒執行一次
        # schedule.every().hour.do(job) #每小時執行一次
        # schedule.every().day.at("17:19").do(job) #每天9點30執行一次
        # schedule.every().monday.do(job) #每週一執行一次
        # schedule.every().wednesday.at("14:45").do(job) #每週三14點45執行一次
        # 無窮迴圈
        while True:
            schedule.run_pending()
            time.sleep(1)

    if re.match("關閉提醒", emsg):
        import schedule
        schedule.clear()

    if message:
        line_bot_api.reply_message(
            event.reply_token,
            message)


@handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))  # 先將postback中的資料轉成字典

    action = data.get('action')  # 再get action裡面的值

    if action == 'checkout':  # 如果action裡面的值是checkout的話才會執行結帳的動作

        user_id = event.source.user_id  # 取得user_id

        cart = Cart(user_id=user_id)  # 透過user_id取得購物車

        if not cart.bucket():  # 判斷購物車裡面有沒有資料，沒有就回傳購物車是空的
            message = TextSendMessage(text='你的購物車是空的.')

            line_bot_api.reply_message(event.reply_token, [message])

            return 'OK'

        order_id = uuid.uuid4().hex  # 如果有訂單的話就會使用uuid的套件來建立，因為它可以建立獨一無二的值

        total = 0  # 總金額
        items = []  # 暫存訂單項目

        for product_name, num in cart.bucket().items():  # 透過迴圈把項目轉成訂單項目物件
            # 透過產品名稱搜尋產品是不是存在
            product = db_session.query(Products).filter(
                Products.name.ilike(product_name)).first()
            # 接著產生訂單項目的物件
            item = Items(product_id=product.id,
                         product_name=product.name,
                         product_price=product.price,
                         order_id=order_id,
                         quantity=num)

            items.append(item)

            total += product.price * int(num)  # 訂單價格 * 訂購數量
        # 訂單項目物件都建立後就會清空購物車
        cart.reset()
        # 建立LinePay的物件
        line_pay = LinePay()
        # 再使用line_pay.pay的方法，最後就會回覆像postman的格式
        info = line_pay.pay(product_name='LSTORE',
                            amount=total,
                            order_id=order_id,
                            product_image_url=Config.STORE_IMAGE_URL)
        # 取得付款連結和transactionId後
        pay_web_url = info['paymentUrl']['web']
        transaction_id = info['transactionId']
        # 接著就會產生訂單
        order = Orders(id=order_id,
                       transaction_id=transaction_id,
                       is_pay=False,
                       amount=total,
                       user_id=user_id)
        # 接著把訂單和訂單項目加入資料庫中
        db_session.add(order)

        for item in items:
            db_session.add(item)

        db_session.commit()
        # 最後告知用戶並提醒付款
        message = TemplateSendMessage(
            alt_text='感謝您的購買, 請堅持付款.',
            template=ButtonsTemplate(
                text='感謝您的購買, 請堅持付款.',
                actions=[
                    URIAction(label='Pay NT${}'.format(order.amount),
                              uri=pay_web_url)
                ]))

        line_bot_api.reply_message(event.reply_token, [message])

    return 'OK'
# 是否追蹤/封鎖(follow or not)

# 監聽 跟隨/解除封鎖(follow or not)
@handler.add(FollowEvent)
def handle_follow(event):
    get_or_create_user(event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='歡迎回來, 悠然美地 o(_ _)o ♥'))

# 監聽 封鎖
@handler.add(UnfollowEvent)
def handle_unfollow():
    print("Got Unfollow event")

# 建立 產品 資料庫
@app.before_first_request
def init_products():
    result = init_db()
    if result:
        init_data = [Products(name='TLC保濕化妝水',
                              product_image_url='https://i.imgur.com/bshv83t.jpg',
                              price=250,
                              description='具有潤澤肌膚、維持肌膚彈性與保濕度以及增加緊實度，使肌膚呈現細緻與透明感、亮麗有光。'),
                     Products(name='TLC玻尿酸精華液',
                              product_image_url='https://i.imgur.com/R7SPtBJ.jpg',
                              price=300,
                              description='能迅速賦予乾荒肌膚潤澤與滋養，徹底改善膚質，增加皮膚的含水，呈現緊緻光亮的肌膚。'),
                     Products(name='TLC保濕乳液',
                              product_image_url='https://i.imgur.com/J4Ydg9H.jpg',
                              price=650,
                              description='提供肌膚所需的保濕，令肌膚细緻有光澤加強肌膚的防禦功能')]
        db_session.bulk_save_objects(init_data)
        db_session.commit()


#主程式啟動###################
if __name__ == "__main__":
    # init_db()
    init_products()
    app.run()
#主程式啟動###################
