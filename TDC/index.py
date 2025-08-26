print(r""" __          ________ ____   _____ _____ _______ ______  
 \ \        / /  ____|  _ \ / ____|_   _|__   __|  ____| 
  \ \  /\  / /| |__  | |_) | (___   | |    | |  | |__    
   \ \/  \/ / |  __| |  _ < \___ \  | |    | |  |  __|   
    \  /\  /  | |____| |_) |____) |_| |_   | |  | |____  
     \/  \/   |______|____/|_____/|_____|  |_|  |______| 
                 |__   __|  __ \ / ____|                 
                    | |  | |  | | |                      
                    | |  | |  | | |                      
                    | |  | |__| | |____                  
                    |_|  |_____/ \_____|
""")
try:
    from TDC import app, login
    from flask import render_template, request, redirect, flash,Response,send_from_directory
    from flask_login import login_user, logout_user, current_user
    from TDC import utils
    from TDC.xu_ly import check_the, mua_key
    import re
    
    @app.route('/favicon.ico')
    def favicon():
        try:
            return send_from_directory('static/img', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
        except Exception as e:
            return render_template('404.html')

    @app.route('/robots.txt')
    def robots_txt():
        try:
            return Response(
                "User-agent: *\nDisallow: /404/\n",
                mimetype='text/plain'
            )
        except Exception as e:
            return render_template('404.html')
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route("/", methods=['GET', 'POST'])
    def home():
        try:
            err_msg = ""
            if request.method == 'POST':
                action = request.form.get('action')
                # Đăng nhập
                if action == 'login':
                    token = request.form.get('cf-turnstile-response')
                    if not utils.verify_turnstile_token(token, request.remote_addr):
                        err_msg = 'Xác minh CAPTCHA thất bại!'
                    else:
                        username = request.form.get('username')
                        password = request.form.get('password')
                        user = utils.login_user(username=username, password=password)
                        if user:
                            login_user(user)
                            return redirect('/')
                        else:
                            err_msg = 'Username hoặc Password sai!!!'
                # Đăng ký tài khoản
                elif action == 'register':
                    token = request.form.get('cf-turnstile-response')
                    if not utils.verify_turnstile_token(token, request.remote_addr):
                        err_msg = 'Xác minh CAPTCHA thất bại!'
                    else:
                        username = request.form.get('username')
                        password = request.form.get('password')
                        email = request.form.get('email')
                        # Username validation: only letters and digits (no special characters, no underscore)
                        if not re.match(r'^[a-zA-Z0-9]+$', username):
                            err_msg = 'Username chỉ được chứa chữ cái và số, không có ký tự đặc biệt!'
                        else:
                            try:
                                if utils.add_user(username=username, password=password, email=email):
                                    flash('Đăng ký thành công!')
                                    return redirect('/')
                                else:
                                    err_msg = 'Trùng Username Hoặc Email !!!'
                            except Exception as ex:
                                err_msg = "Lỗi:" + str(ex)
                # Nạp thẻ cào
                elif action == 'nap_the':
                    token = request.form.get('cf-turnstile-response')
                    if not utils.verify_turnstile_token(token, request.remote_addr):
                        err_msg = 'Xác minh CAPTCHA thất bại!'
                    else:
                        loai_the = request.form.get('loaithe')
                        menh_gia = request.form.get('menhgia')
                        ma_the = request.form.get('mathe')
                        seri = request.form.get('seri')
                        if current_user.is_authenticated:
                            username = current_user.username
                            err_msg = check_the(loai_the, menh_gia, ma_the, seri, utils, username)
                        else:
                            err_msg = "Bạn cần đăng nhập"
                elif action == 'mua':
                    if current_user.is_authenticated:
                        username = current_user.username
                        tien = current_user.tien
                        err_msg = mua_key(tien=tien, username=username, utils=utils)
                    else:
                        err_msg = "Bạn cần đăng nhập"
                elif action == 'qmk':
                    token = request.form.get('cf-turnstile-response')
                    if not utils.verify_turnstile_token(token, request.remote_addr):
                        err_msg = 'Xác minh CAPTCHA thất bại!'
                    else:
                        username = request.form.get('username')
                        err_msg = utils.mail(username=username)
                # Đổi mật khẩu
                elif action == 'dp':
                    if current_user.is_authenticated:
                        token = request.form.get('cf-turnstile-response')
                        if not utils.verify_turnstile_token(token, request.remote_addr):
                            err_msg = 'Xác minh CAPTCHA thất bại!'
                        else:
                            username = current_user.username
                            new_password = request.form.get('password')
                            err_msg = utils.doi_password(username=username, new_password=new_password)
                    else:
                        err_msg = "Bạn cần đăng nhập"
                if err_msg:
                    flash(err_msg)
            if current_user.is_authenticated:
                username = current_user.username
                bd = utils.biendong(username=username)
                nt = utils.napthe(username=username)
                return render_template('index.html', bd=bd, nt=nt, username=username)
            else:
                return render_template('index.html', nt=None)
        except Exception as e:
            return render_template('500.html')

    @app.route('/ctv', methods=['GET', 'POST'])
    def ctv():
        try:
            if not current_user.is_authenticated:
                return redirect("/")
            if current_user.quyen == 'Admin' or current_user.quyen == 'CTV':
                err_msg = ""
                if request.method == 'POST':
                        username = current_user.username
                        userkhach = request.form.get('userkhach')
                        tien = request.form.get('tien')
                        err_msg = utils.doanhthuctv(username=username, userkhach=userkhach, tien=tien)
                ctv= utils.tienctv(username=current_user.username)
                return render_template('ctv.html', err_msg=err_msg,ctv=ctv)
            else:
                return redirect('/')
        except Exception as e:
            return render_template('500.html')

    @login.user_loader
    def user_load(user_id):
        return utils.get_user_by_id(user_id=user_id)

    @app.route('/user_logout')
    def user_signout():
        logout_user()
        return redirect('/')

    if __name__ == '__main__':
        app.run(host="0.0.0.0")
except Exception as e:
    print("Error:", type(e).__name__, "-", e)