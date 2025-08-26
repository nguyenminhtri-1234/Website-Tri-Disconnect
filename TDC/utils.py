import random, datetime, smtplib, threading, os, requests
from typing import Optional
from TDC import app, db
from TDC.models import User, nap_the_cao, bien_dong, kich_hoat_tk, quan_ly_key, doanh_thu_ctv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.zoho.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASS = os.environ.get('EMAIL_PASS', '')

MIN_MUA_AMOUNT = 25000
MAIL_RESEND_INTERVAL_MINUTES = 30
TIMEOUT = 2
salt = bcrypt.gensalt(rounds=10)


def add_user(username: str, password: str, **kwargs) -> bool:
    username = username.strip()
    password_hash = bcrypt.hashpw(password.strip().encode('utf-8'), salt).decode().replace("$2b$", "$2y$")
    email = kwargs.get('email')
    lock = threading.Lock()
    with lock:
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user or existing_email:
            return False
        user = User(username=username, password=password_hash, email=email)
        db.session.add(user)
        db.session.commit()
    return True

def login_user(username: str, password: str, **kwargs) -> Optional[User]:
    if username and password:
        user = User.query.filter_by(username=username.strip()).first()
        if user and bcrypt.checkpw(password.strip().encode('utf-8'), (user.password).encode('utf-8')):
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[User]:
    return User.query.get(user_id)

def nap(loai_the: str, menh_gia: str, ma_the: str, seri: str, username: str) -> str:
    loai_the = loai_the.strip()
    menh_gia = menh_gia.strip()
    ma_the = ma_the.strip()
    seri = seri.strip()
    # Chống trùng số seri hoặc mã thẻ nếu cùng loại thẻ
    if nap_the_cao.query.filter(
        ((nap_the_cao.ma_the == ma_the) | (nap_the_cao.seri == seri)) &
        (nap_the_cao.loai_the == loai_the)
    ).first():
        return 'Mã thẻ hoặc số seri đã được sử dụng cho loại thẻ này!'
    ma_thanh_toan = random.randint(100000, 999999)
    lsu_nap = nap_the_cao(
        username=str(username.strip()),
        trang_thai='Đang xử Lý',
        ma_tt=int(ma_thanh_toan),
        ma_the=str(ma_the),
        seri=str(seri),
        menh_gia=int(menh_gia),
        loai_the=str(loai_the),
        tien=0
    )
    db.session.add(lsu_nap)
    db.session.commit()
    return 'Đang Xử Lý!!!'

def mua(username: str, tien: int) -> str:
    if kich_hoat_tk.query.filter_by(username=username.strip()).first():
        return "Tài khoản của bạn đã được kích hoạt vĩnh viễn."
    username = username.strip()
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Tài khoản không tồn tại."
    if user.tien < MIN_MUA_AMOUNT:
        return "Số dư không đủ để mua gói vĩnh viễn."
    user.tien -= MIN_MUA_AMOUNT
    khtk = kich_hoat_tk(username=username, password=user.password)
    qlk= quan_ly_key(username=username)
    bd = bien_dong(username=username, tien=MIN_MUA_AMOUNT, noi_dung='Mua gói vĩnh viễn')
    db.session.add(bd)
    db.session.add(khtk)
    db.session.add(qlk)
    db.session.commit()
    return 'Mua thành công!!! Vui lòng tải và đăng nhập sử dụng phần mềm'
def doanhthuctv(username: str,userkhach: str, tien: int):
    username = username.strip()
    userkhanh = userkhach.strip()
    tien= int(tien)
    user = User.query.filter_by(username=userkhanh).first()
    dt=doanh_thu_ctv.query.filter_by(username=username).first()
    if not user:
        return "Tài khoản không tồn tại."
    else:
        user.tien += tien
        dt.tien += tien
        hh=tien *0.2
        dt.hoa_hong+= hh
        dt.sodd += 1
        bd = bien_dong(username=userkhanh, tien=tien, noi_dung=f'Nhận tiền từ {username}')
    db.session.add(bd)
    db.session.commit()
    return 'Giao dịch thành công!!!'

def biendong(username: str):
    return bien_dong.query.filter_by(username=username)

def napthe(username: str):
    return nap_the_cao.query.filter_by(username=username)
def tienctv(username: str):
    return doanh_thu_ctv.query.filter_by(username=username)

def doi_password(username: str, new_password: str) -> str:
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Tài khoản không tồn tại!"
    user.password = bcrypt.hashpw(new_password.strip().encode('utf-8'), salt).decode().replace("$2b$", "$2y$")
    # Update password in kich_hoat_tk if exists
    khtk = kich_hoat_tk.query.filter_by(username=username).first()
    if khtk:
        khtk.password = user.password
    db.session.commit()
    return "Đổi mật khẩu thành công!!!"
def activate(username, password, uuid):
    if not username or not password or not uuid:
        return {"status": "error_missing_fields"}
    username = username.strip()
    password = password.strip()
    uuid = uuid
    try:
        existing_account = kich_hoat_tk.query.filter_by(username=username).first()
        if existing_account and bcrypt.checkpw((existing_account.password).encode('utf-8'), password.encode('utf-8')):
            t2_acc = quan_ly_key.query.filter_by(username=username).first()
            if not t2_acc:
                return {"status": "error_no_key"}
            try:
                tg = datetime.datetime.strptime(t2_acc.date, '%Y-%m-%d %H:%M:%S.%f')
            except Exception:
                tg = datetime.datetime.now() - datetime.timedelta(minutes=TIMEOUT + 1)
            if t2_acc.uuid == uuid or tg < datetime.datetime.now() - datetime.timedelta(minutes=TIMEOUT):
                t2_acc.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                t2_acc.uuid = uuid
                db.session.commit()
                return {"status": "success"}
            else:
                return {"status": "error"}
        else:
            return {"status": "error"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
def send_mail_async(to_email, msg):
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
    except Exception as e:
        app.logger.error(f"Mail send error: {e}")

def mail(username: str) -> str:
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Tài khoản không tồn tại!"
    try:
        last_mail_time = datetime.datetime.strptime(user.date_mail, '%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        last_mail_time = datetime.datetime.min
    if last_mail_time > datetime.datetime.utcnow() - datetime.timedelta(minutes=MAIL_RESEND_INTERVAL_MINUTES):
        return f"Bạn đã gửi email quá nhanh, vui lòng đợi {MAIL_RESEND_INTERVAL_MINUTES} phút trước khi gửi lại!"
    user.date_mail = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    password = str(random.randint(100000, 999999))
    user.password = bcrypt.hashpw(password, salt)
    db.session.commit()
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = user.email
    msg['Subject'] = "Gửi lại mật khẩu"
    body = f"Mật khẩu của bạn là: {password}"
    msg.attach(MIMEText(body, 'plain'))
    threading.Thread(
        target=send_mail_async,
        args=(user.email, msg)
    ).start()

    return "✅ Gửi email thành công!"
def verify_turnstile_token(token, remote_ip):
    SECRET_KEY = ''  # thay bằng key của bạn
    resp = requests.post(
        'https://challenges.cloudflare.com/turnstile/v0/siteverify',
        data={
            'secret': SECRET_KEY,
            'response': token,
            'remoteip': remote_ip
        }
    )
    return resp.json().get('success', False)
