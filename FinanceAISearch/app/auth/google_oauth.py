from flask import redirect, request, url_for
from oauthlib.oauth2 import WebApplicationClient
import requests
from ..models import db, User
from flask_login import login_user
from ..config import Config

config = Config()
client = WebApplicationClient(config.GOOGLE_CLIENT_ID)

def google_login():
    google_provider_cfg = requests.get(config.GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('auth.google_callback', _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

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
            user = User(username=users_name, email=users_email, google_id=unique_id)
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for("index"))
    else:
        return "User email not available or not verified by Google.", 400
