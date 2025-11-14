# app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import db
# db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=True)  # 允许为空，支持第三方登录
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    clerk_id = db.Column(db.String(100), unique=True,nullable=True)  # 新增 clerk_id
    # 认证类型：local, google, clerk
    auth_type = db.Column(db.String(20), default='local')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    messages = db.relationship('Message', back_populates='conversation')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    role = db.Column(db.String(10))  # 'user' or 'assistant'
    content = db.Column(db.Text)
    conversation = db.relationship('Conversation', back_populates='messages')
    related_question = db.relationship("RelatedQuestion", back_populates="messages")


class RelatedQuestion(db.Model):
    __tablename__ = 'related_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    messages_id = db.Column(db.Integer, db.ForeignKey('messages.id'))  # 添加外键
    messages = db.relationship('Message', back_populates='related_question') 

    
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # 关联用户ID
    language = db.Column(db.String(50), nullable=True)
    personal_info = db.Column(db.String(200), nullable=True)
    preset_prompts = db.Column(db.Text, nullable=True)  # 存储为逗号分隔的字符串

    def __repr__(self):
        return f'<UserPreferences {self.user_id}>'