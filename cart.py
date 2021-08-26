from cachelib import SimpleCache
from linebot.models import *
from database import db_session  # 資料系結
from product import Products  # 資料系結 class Products

cache = SimpleCache()

class Cart(object):
        def __init__(self,user_id):
            self.cache=cache
            self.user_id = user_id

        def bucket(self):
            return cache.get(key=self.user_id) or {}

        def add(self,product,num):
            bucket=cache.get(key=self.user_id)
            if bucket == None:
                cache.add(key=self.user_id,value={product: int(num)})

            else:
                bucket.update({product: int(num)})
                cache.set(key=self.user_id,value=bucket)

        def reset(self):
            cache.set(key=self.user_id,value={})


        def display(self):  # 計算購物車內容及價格
            total = 0  # 總金額
            product_box_component = []  # 放置產品明細

            for product_name, num in self.bucket().items():  # 透過for迴圈抓取購物車內容
                # 透過 Products.name 去搜尋
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
                amount = product.price * int(num)  # 然後再乘以購買的數量
                total += amount
                # 透過 TextComponent 顯示產品明細，透過BoxComponent包起來，再append到product_box_component中
                product_box_component.append(BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text='{num} x {product}'.format(num=num,
                                                                      product=product_name),
                                      size='sm', color='#555555', flex=0),
                        TextComponent(text='NT$ {amount}'.format(amount=amount),
                                      size='sm', color='#111111', align='end')]
                ))

            bubble = BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        BoxComponent(
                            layout='baseline',
                            margin='xxl',
                            spacing='sm',
                            contents=[
                                # parent element 必須為 baseline
                                IconComponent(size='xl',url='https://i.imgur.com/1TmnC5Y.png'),
                                TextComponent(text='以下是您訂購的商品',wrap=True,size='lg',margin='md',align='center'),
                                IconComponent(size='xl', url='https://i.imgur.com/1TmnC5Y.png')
                            ]
                        ),
                        SeparatorComponent(margin='xxl'),  # 顯示分隔線
                        BoxComponent(
                            layout='vertical',
                            margin='xxl',
                            spacing='md',
                            contents=product_box_component
                        ),
                        SeparatorComponent(margin='xxl'),
                        BoxComponent(
                            layout='vertical',
                            margin='xxl',
                            spacing='sm',
                            contents=[
                                BoxComponent(
                                    layout='horizontal',
                                    contents=[
                                        TextComponent(text='TOTAL',
                                                      size='md',
                                                      color='#555555',
                                                      flex=0),
                                        TextComponent(text='NT$ {total}'.format(total=total),
                                                      size='md',
                                                      weight='bold',
                                                      color='#111111',
                                                      align='end')]
                                )

                            ]
                        ),
                        SeparatorComponent(margin='xxl')
                    ],
                ),
                footer=BoxComponent(  # 最底端的地方
                    layout='vertical',
                    spacing='md',
                    contents=[
                        ButtonComponent(
                            style='primary',
                            color='#f09ba0',
                            action=PostbackAction(label='Checkout',
                                                  display_text='checkout',
                                                  data='action=checkout')
                        ),
                        BoxComponent(
                            layout='horizontal',
                            spacing='md',
                            contents=[
                                ButtonComponent(
                                    style='primary',
                                    color='#cc9c9e',
                                    height='sm',
                                    flex=3,
                                    action=MessageAction(label='清空、重新訂購',
                                                         text='empty cart'),
                                ),
                                ButtonComponent(
                                    style='primary',
                                    color='#cc9c9e',
                                    height='sm',
                                    flex=2,
                                    action=MessageAction(label='還想加購',
                                                         text='add'),
                                )
                            ]

                        )
                    ]
                )
            )

            message = FlexSendMessage(alt_text='Cart', contents=bubble)

            return message  # 會回傳到app.py message = cart.display()

#cart = Cart( user_id='10')
#cart.bucket()
#cart.add('Coffee',2)
#cart.reset()
#cart.display()