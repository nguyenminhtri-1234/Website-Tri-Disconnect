from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from TDC import db, app
from datetime import datetime
from flask_login import UserMixin, current_user
from typing import Optional

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id}>'

#tai khoan
class User(BaseModel, UserMixin):
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(512), nullable=False)  # Increased length for password hash
    email = Column(String(255), unique=True, nullable=False)
    tien = Column(Integer, default=0)
    trang_thai = Column(Boolean, default=True)
    date = Column(DateTime, default=datetime.utcnow)
    quyen = Column(String(10), default='User')
    date_mail = Column(String(255), default='2020-01-01 00:00:00.000000')
    def __repr__(self):
        return f'<User {self.username}>'

#log nap the
class nap_the_cao(BaseModel):
    username = Column(String(150), nullable=False)
    ma_the = Column(String(20), nullable=False)
    seri = Column(String(20), nullable=False)
    menh_gia = Column(Integer, nullable=False)
    loai_the = Column(String(10), nullable=False)
    trang_thai = Column(String(255), nullable=False)
    ma_tt = Column(Integer, nullable=False)
    tien = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<nap_the_cao {self.username} {self.menh_gia}>'
# Nạp tiền vào tài khoản qua ngân hàng
class nap_ngan_hang(BaseModel):
    username = Column(String(150), nullable=False)
    ma_ck = Column(String(128), nullable=False)
    tien = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(String(255))
    def __repr__(self):
        return f'<nap_ngan_hang {self.username} {self.tien}>'
#lich su  bien dong
class bien_dong(BaseModel):
    username = Column(String(150), nullable=False)
    noi_dung = Column(String(255), nullable=False)
    tien = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<bien_dong {self.username} {self.tien}>'

#Kích hoạt tài khoản
class kich_hoat_tk(BaseModel):
    username = Column(String(150), nullable=False)
    password = Column(String(512), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    trangthai = Column(String(50), default='Yes')
    note = Column(String(255))
    def __repr__(self):
        return f'<kich_hoat_tk {self.username}>'

class quan_ly_key(BaseModel):
    username = Column(String(150), nullable=False)
    uuid = Column(String(150))
    date = Column(String(255), default='2020-01-01 00:00:00.000000')
    note = Column(String(255))
    def __repr__(self):
        return f'<quan_ly_Key {self.username}>'
# Doanh thu của CTV
class doanh_thu_ctv(BaseModel):
    username = Column(String(150), nullable=False)
    tien = Column(Integer, default=0)
    hoa_hong = Column(Integer, default=0)
    sodd= Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(String(255))
    def __repr__(self):
        return f'<doanh_thu {self.username} {self.tien}>'

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()