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
CORS(auth_bp)

auth_bp = Blueprint('auth', __name__)

client = WebApplicationClient(config.GOOGLE_CLIENT_ID)

CORS(auth_bp)

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
    print(data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    query_sql = "SELECT * from `user` where username = \"{username}\";".format(username=username)

    result = tm.execute_sql(query_sql, is_query=True)
    if len(result)>0:
        return jsonify({"message": "User already exists","code":400}), 200
    hashed_password = ck.hash_password(password)
    insert_sql = "INSERT INTO `user` (username, password,email) VALUES (\'{username}\', \'{password}\',\'{email}\');".format(username=username,password=hashed_password,email=email)

    status = tm.execute_sql(insert_sql, is_query=False)
    if status:
        return jsonify({"message": "User registered successfully","code":200}), 200
    else:
        return jsonify({"message": "database error","code":502}), 200


@auth_bp.route('/login_my', methods=['POST'])
def login_my():
    data = request.json
    print(data)
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    query_sql = "SELECT * from `user` where email = \"{username}\";".format(username=email)

    result = tm.execute_sql(query_sql, is_query=True)
    if len(result)==0:
        return jsonify({"message": "Account error","code":403}), 200
    print(result)
    check_pw = result[0]["password"]
    if ck.check_password(check_pw,password):
        token = tk.generate_token_email(email)
            # 返回用户信息和 JWT 令牌
        return jsonify({
            "message": "Logged in successfully",
            "user": {
                "id": result[0]["id"],
                "username": result[0]["username"]
            },
            "token": token,
            "code":200
        }), 200

    else:
        return jsonify({"message": "Login error", "code": 403}), 200

@auth_bp.route('/search_users', methods=['POST','GET'])
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
