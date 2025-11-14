from functools import wraps
from datetime import datetime, timedelta
import secrets
from flask import Flask, request, make_response
import json
import jwt
from flask import jsonify
from json.decoder import JSONDecodeError
import redis
redis_client = redis.Redis(host='39.99.237.144', port=6379, db=0,password=6050121)

token_store = {}
SECRET_KEY = 'your-secret-key'

def generate_token():
    """生成一个新的token,并存储其过期时间."""
    redis_client = redis.Redis(host='39.99.237.144', port=6379, db=0, password=6050121)

    # token = secrets.token_hex(16)  # 生成一个随机的16字节的十六进制字符串
    # expiration_time = datetime.now() + timedelta(days=5)
    # token_store[token] = expiration_time
    token = secrets.token_hex(16)  # 生成一个随机的16字节的十六进制字符串
    expiration_time = datetime.now() + timedelta(days=5)
    # 将 token 和过期时间存入 Redis
    redis_client.set(token, str(expiration_time.timestamp()), ex=int(timedelta(days=5).total_seconds()))
    return token


def generate_token_email(email):
    """生成一个新的包含邮箱的JWT token"""
    try:
        expiration = datetime.now() + timedelta(days=1)
        token_data = {
            'email': email,
            'exp': expiration.timestamp()
        }

        # 将数据存入 Redis
        token = secrets.token_hex(16)
        redis_client.set(
            token,
            json.dumps(token_data),
            ex=int(timedelta(days=1).total_seconds())
        )

        return token
    except Exception as e:
        print(f"Token generation error: {str(e)}")
        return None


# def token_required_bak(f):
#     """装饰器:检查请求中的token是否有效."""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('X-Token')
#         if not token or token not in token_store:
#             return make_response({"error": "Token is missing or invalid.","code":401}, 200)
#         if datetime.now() > token_store[token]:
#             del token_store[token]
#             return make_response({"error": "Token has expired.","code":401}, 200)
#         return f(*args, **kwargs)
#     return decorated


def token_required(f):
    """装饰器:检查请求中的 token 是否有效."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token')

        if not token:
            return jsonify({"error": "Token is missing.", "code": 401}), 401

        try:
            # 首先尝试从 Redis 中获取 token 数据
            token_data_str = redis_client.get(token)
            if token_data_str:
                token_data = json.loads(token_data_str)
                if not isinstance(token_data, dict) or 'email' not in token_data:
                    raise ValueError("Invalid token data format from Redis.")
                email = token_data.get('email')
            else:
                email = decode_token(token)

            if email is None:
                return jsonify({"error": "Token is invalid or has expired.", "code": 401}), 401

            # 将 email 作为上下文传递给被装饰函数
            kwargs['email'] = email

            # 调用被装饰的函数
            return f(*args, **kwargs)

        except ValueError as ve:
            return jsonify({"error": str(ve), "code": 400}), 400
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}", "code": 500}), 500

    return decorated


def decode_token(token):
    """解码 JWT token 并返回其中的 email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        email = payload.get('email')
        if email is None:
            return None
        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_token(token):
    """从请求头部中解码 JWT token 并返回其中的 email."""

    # token = header.get('X-Token')

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        email = payload.get('email')
        if email is None:
            return None
        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """装饰器:检查请求中的 token 是否有效."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Token')
        print(token)

        if not token:
            return jsonify({"error": "Token is missing.", "code": 401}), 401

        try:
            # 首先尝试从 Redis 中获取 token 数据
            token_data_str = redis_client.get(token)
            if token_data_str:
                token_data = json.loads(token_data_str)
                if not isinstance(token_data, dict) or 'email' not in token_data:
                    raise ValueError("Invalid token data format from Redis.")
                email = token_data.get('email')
            else:
                email = decode_token(token)

            if email is None:
                return jsonify({"error": "Token is invalid or has expired.", "code": 401}), 401

            # 将 email 存储在全局变量中
            # global email_context
            # email_context['email'] = email

            # 调用被装饰的函数
            return f(*args, **kwargs)

        except ValueError as ve:
            return jsonify({"error": str(ve), "code": 400}), 400
        # except Exception as e:
        #     return jsonify({"error": f"An unexpected error occurred: {str(e)}", "code": 500}), 500

    return decorated