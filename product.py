from sqlalchemy import Column, String, Integer
from linebot.models import *
from database import Base, db_session
from urllib.parse import quote #避免使用者 按到空白建
from config import Config


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)  # 產品名
    price = Column(Integer)  # 價格
    description = Column(String)  # 說明
    product_image_url = Column(String)  # 圖片

#列出所有的產品
    @staticmethod
    def list_all():
        products = db_session.query(Products).all()#抓取資料庫中所有產品的資料

        bubbles = []

        for product in products:
            bubble = BubbleContainer(
                hero=ImageComponent(
                    size='full',
                    aspect_ratio='20:20',
                    aspect_mode='cover',
                    url=product.product_image_url
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text=product.name,#產品名稱
                                      wrap=True,
                                      weight='bold',
                                      size='lg'),
                        BoxComponent(#產品價格
                            layout='baseline',
                            contents=[#利用format的方法把product.price轉換成字串
                                TextComponent(text='NT${price}'.format(price=product.price),
                                              wrap=True,
                                              weight='bold',
                                              size='lg')
                            ]
                        ),
                        TextComponent(margin='md',#產品敘述 如果product.description or ''是空值的話就直接回傳空字串
                                      text='{des}'.format(des=product.description or ''),
                                      wrap=True,
                                      weight='bold',
                                      size='xs',
                                      color='#aaaaaa')
                    ],
                ),
                footer=BoxComponent(#購物車按鈕
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        BoxComponent(  # 購物車按鈕
                            layout='horizontal',
                            spacing='sm',
                            contents=[
                                ButtonComponent(
                                    style='primary',
                                    color='#f09ba0',
                                    height='sm',
                                    margin='none',
                                    action=URIAction(label='快速購買 (1入)',
                                                     uri='line://oaMessage/{base_id}/?{message}'.format(
                                                         base_id=Config.BASE_ID,
                                                         message=quote(
                                                             "{product}, 想訂購數量:1".format(product=product.name))))),
                                ButtonComponent(
                                    style='primary',
                                    color='#f09ba0',
                                    height='sm',
                                    margin='md',
                                    action=MessageAction(label='查看購物車',
                                                            text='my cart'))
                            ]),
                        BoxComponent(  # 購物車按鈕
                            layout='vertical',
                            spacing='sm',
                            contents=[
                                ButtonComponent(
                                    style='primary',
                                    color='#f09ba0',
                                    height='sm',
                                    margin='md',
                                    action=URIAction(label='輸入數量',
                                                     uri='line://oaMessage/{base_id}/?{message}'.format(
                                                         base_id=Config.BASE_ID,
                                                         message=quote(
                                                             "{product}, 想訂購數量:".format(product=product.name)))))
                            ])
                    ]
                )
            )

            bubbles.append(bubble)

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='products', contents=carousel_container)

        return message