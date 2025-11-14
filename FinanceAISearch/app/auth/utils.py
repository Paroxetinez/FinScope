import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from ..config import Config

config = Config()

def generate_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")
    return token
