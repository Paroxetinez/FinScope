from flask import Blueprint, request, jsonify, redirect, url_for, session,Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from oauthlib.oauth2 import WebApplicationClient
import requests
import app.tool_mysql as tm
import app.check as ck
import app.my_token as tk
from flask_cors import CORS
from .config import Config
config = Config()

auth_bp = Blueprint('auth', __name__)

client = WebApplicationClient(config.GOOGLE_CLIENT_ID)

app = Flask(__name__)
CORS(auth_bp)  # 这将为所有路由启用CORS

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
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    clerk_id = data.get('clerk_id')  # 新增 clerk_id
    auth_type = data.get('auth_type', 'local')  # 新增 auth_type

    # 检查用户是否已存在
    query_sql = "SELECT * FROM `user` WHERE email = %s"
    result = tm.execute_sql(query_sql, (email,), is_query=True)

    if len(result) > 0:
        # 如果是 Clerk 用户，更新 clerk_id
        if auth_type == 'clerk':
            update_sql = """
                UPDATE `user` 
                SET clerk_id = %s, auth_type = 'clerk' 
                WHERE email = %s
            """
            tm.execute_sql(update_sql, (clerk_id, email), is_query=False)
            return jsonify({"message": "User updated successfully", "code": 200}), 200
        return jsonify({"message": "User already exists", "code": 400}), 200

    # 创建新用户
    if auth_type == 'clerk':
        insert_sql = """
            INSERT INTO `user` (username, email, clerk_id, auth_type) 
            VALUES (%s, %s, %s, 'clerk')
        """
        status = tm.execute_sql(
            insert_sql, (username, email, clerk_id), is_query=False)
    else:
        hashed_password = ck.hash_password(password)
        insert_sql = """
            INSERT INTO `user` (username, password, email, auth_type) 
            VALUES (%s, %s, %s, 'local')
        """
        status = tm.execute_sql(
            insert_sql, (username, hashed_password, email), is_query=False)

    if status:
        return jsonify({"message": "User registered successfully", "code": 200}), 200
    else:
        return jsonify({"message": "Database error", "code": 502}), 200


@auth_bp.route('/login_my', methods=['POST'])
def login_my():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    clerk_id = data.get('clerk_id')

    # Clerk 登录处理
    if clerk_id:
        query_sql = "SELECT * FROM `user` WHERE email = %s AND clerk_id = %s"
        result = tm.execute_sql(query_sql, (email, clerk_id), is_query=True)
    else:
        # 原有的密码登录逻辑
        query_sql = "SELECT * FROM `user` WHERE email = %s"
        result = tm.execute_sql(query_sql, (email,), is_query=True)

    if len(result) == 0:
        return jsonify({"message": "Account error", "code": 403}), 200

    if clerk_id:
        # Clerk 用户直接通过验证
        token = tk.generate_token_email(email)
        return jsonify({
            "message": "Logged in successfully",
            "user": {
                "id": result[0]["id"],
                "username": result[0]["username"]
            },
            "token": token,
            "code": 200
        }), 200
    else:
        # 原有的密码验证逻辑
        check_pw = result[0]["password"]
        if check_pw and ck.check_password(check_pw, password):
            token = tk.generate_token_email(email)
            return jsonify({
                "message": "Logged in successfully",
                "user": {
                    "id": result[0]["id"],
                    "username": result[0]["username"]
                },
                "token": token,
                "code": 200
            }), 200
        else:
            return jsonify({"message": "Login error", "code": 403}), 200
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

@auth_bp.route('/login/google')
def google_login():
    google_provider_cfg = requests.get(config.GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('auth.google_callback', _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/login/google/callback')
def google_callback():
    google_provider_cfg = requests.get(config.GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    code = request.args.get("code")

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["name"]

        user = User.query.filter_by(email=users_email).first()

        if not user:
            user = User(
                username=users_name,
                email=users_email,
                google_id=unique_id
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)

        return redirect(url_for("index"))
    else:
        return "User email not available or not verified by Google.", 400
