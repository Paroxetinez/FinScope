from flask import request, jsonify, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth_bp
from ..models import db, User
from .google_oauth import google_login, google_callback
from .utils import generate_token
import requests
import app.tool_mysql as tm
import secrets
import app.check as ck
import app.my_token as tk
from flask_cors import CORS
from oauthlib.oauth2 import WebApplicationClient
from datetime import datetime, timedelta
CORS(auth_bp)
  # 这将为所有路由启用CORS
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
    
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/register_my', methods=['POST'])
def register_my():
    try:
        data = request.json
        email = data.get('email')
        username = data.get('username')
        clerk_id = data.get('clerk_id')

        # 检查用户是否已存在
        existing_user = User.query.filter(
            (User.email == email) | (User.clerk_id == clerk_id)
        ).first()

        if existing_user:
            return jsonify({
                "code": 400,
                "message": "用户已存在"
            })

        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            clerk_id=clerk_id
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": "注册成功"
        })

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}"
        }), 500


@auth_bp.route('/login_my', methods=['POST', 'OPTIONS'])
def login_my():
    if request.method == 'OPTIONS':
        # 处理预检请求
        return '', 200
    try:
        data = request.json
        email = data.get('email')
        clerk_id = data.get('clerk_id')

        # 通过 email 或 clerk_id 查找用户
        user = User.query.filter(
            (User.email == email) | (User.clerk_id == clerk_id)
        ).first()

        if not user:
            return jsonify({
                "code": 400,
                "message": "用户不存在"
            })

        # 生成 token
        token = tk.generate_token_email(user.email)

        return jsonify({
            "code": 200,
            "token": token,
            "user": user.to_dict(),
            "message": "Login Success"
        })

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}"
        }), 500
        
@auth_bp.route('/search_users', methods=['POST'])
def search():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    query_sql = "SELECT * from `user` where email = \"{username}\";".format(username=email)

    result = tm.execute_sql(query_sql, is_query=True)
    return jsonify({"code": 200, "data": {"user": result}}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 400

    login_user(user)
    # 返回用户信息和 JWT 令牌
    return jsonify({
        "message": "Logged in successfully",
        "user": {
            "id": user.id,
            "username": user.username
        },
        "access_token": access_token
    }), 200

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
# 使用ProxyFix中间件

# 配置 OAuth 2.0 客户端
client_id = ''
client_secret = ''
client = WebApplicationClient(client_id)

token_store = {}

def get_google_provider_cfg():
    return requests.get('https://accounts.google.com/.well-known/openid-configuration').json()

@auth_bp.route('/login/google',methods=['GET','POST'])
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for("auth.callback", _external=True, _scheme='https'),  # 确保使用HTTPS
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

def generate_token():
    """生成一个新的token,并存储其过期时间."""
    token = secrets.token_hex(16)  # 生成一个随机的16字节的十六进制字符串
    expiration_time = datetime.now() + timedelta(days=5)
    token_store[token] = expiration_time
    return token


@auth_bp.route("/login/google/authorized", methods=['GET','POST'])
def callback():
    # 获取授权码
    code = request.args.get("code")
    print(code)
    
    # 获取 Google 提供商的配置
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # 准备请求以获取访问令牌
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    # 发送请求以获取访问令牌
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(client_id, client_secret),
    )
    # 检查访问令牌请求是否成功
    if token_response.status_code != 200:
        return jsonify({"error": "Failed to retrieve access token123"}), 400

    # 解析访问令牌响应
    client.parse_request_body_response(token_response.text)

    # 获取用户信息端点
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    # 使用访问令牌准备请求用户信息
    uri, headers, body = client.add_token(userinfo_endpoint)
    # 发送请求以获取用户信息
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # 检查用户信息请求是否成功且电子邮件已验证
    if userinfo_response.status_code == 200 and userinfo_response.json().get("email_verified"):
        user_info = userinfo_response.json()
        # 将用户信息存储在会话中
        session["user"] = {
            "unique_id": user_info["sub"],
            "name": user_info["given_name"],
            "email": user_info["email"],
            "profile_pic": user_info["picture"],
        }

        # 生成一个新的token并包含在响应中
        token = generate_token()

        return jsonify({
            "message": "321Login successful",
            "code": 200,
            "token": token,
            "user": session["user"]
        }), 200

    else:
        # 处理登录失败的情况
        return jsonify({
            "message": "Login failed",
            "code": 400
        }), 400

# # Google OAuth 路由
# auth_bp.add_url_rule('/login/google', 'google_login', google_login)
# auth_bp.add_url_rule('/login/google/callback', 'google_callback', google_callback)
