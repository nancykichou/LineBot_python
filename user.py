# -*- coding: utf-8 -*-
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)  # line 用戶ID
    nick_name = Column(String)  # Line用戶 name
    image_url = Column(String(length=256))  # Line用戶 大頭貼
    created_time = Column(DateTime, default=func.now())  # Line用戶 被資料顧建立時間
