def check_the(loai_the,menh_gia,ma_the,seri,utils,username):
    if loai_the.strip() == 'loi':
        err_msg = "Nhập sai vui lòng nhập lại!!!"
    elif menh_gia.strip() == 'loi':
        err_msg = "Nhập sai vui lòng nhập lại!!!"
    elif 7>len(ma_the.strip()) or len(ma_the.strip())>17:
        err_msg = "Nhập sai vui lòng nhập lại!!!"
    elif 7> len(seri.strip()) or len(seri.strip()) > 17:
        err_msg = "Nhập sai vui lòng nhập lại!!!"
    elif ma_the.strip()== seri.strip():
        err_msg = "Nhập sai vui lòng nhập lại!!!"
    else:
        a = ["VIETTEL", "VINAPHONE", "MOBIFONE", "GATE", "ZING", "MEGACARD", "BIT", "GARENA"]
        b = ["10000", "20000", "30000", "50000", "100000", "200000", "300000", "500000", "1000000"]
        if menh_gia in b:
            if loai_the in a:
                err_msg = utils.nap(loai_the, menh_gia, ma_the, seri, username)
            else:
                err_msg = 'quát tờ phất!!!'
        else:
            err_msg = 'quát tờ phất!!!'
    return err_msg
def mua_key(tien, username, utils):
    if tien < 25000:
        err_msg = "Số tiền trong tài khoản không đủ để thực hiện. Vui lòng nạp thêm tiền."
    else:
        err_msg = utils.mua(username=username, tien=tien)
    return err_msg