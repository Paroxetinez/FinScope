import logging
from flask import Blueprint, request, jsonify, send_from_directory
from app.models import User, Conversation, Message, RelatedQuestion, db
from app.chat import chat_with_gpt, chat_with_mygpt, extract_info_from_conversation, rag_chat
from app.my_token import token_required
import app.my_token as tk
import app.tool_mysql as tm
import re
from .models import User, Conversation, Message, UserPreferences, RelatedQuestion  # 确保引入了你的模型类
from flask_cors import CORS
import markdown
from sqlalchemy.orm import joinedload
from flask import Response, stream_with_context
import time
import json
from flask import Flask
import requests
from app.event_analyse import analyze_event  # 添加这一行
from .twitter_publisher import TwitterPublisher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建一个蓝图
api_bp = Blueprint('api', __name__)
CORS(api_bp)  # 这将为所有路由启用CORS


@api_bp.route('/')
def index():
    return send_from_directory('static', 'index.html')


# PayPal 配置
CLIENT_ID = ""
CLIENT_SECRET = ""
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  # 沙盒环境


@api_bp.route('/create-order', methods=['POST'])
def create_order():
    # 从 PayPal 获取访问令牌
    auth_response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    auth_response.raise_for_status()
    access_token = auth_response.json()["access_token"]

    # 创建订单
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "10.00",  # 订单金额
                }
            }
        ]
    }
    order_response = requests.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders",
        json=order_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    order_response.raise_for_status()
    return jsonify(order_response.json())


@api_bp.route('/capture-order/<order_id>', methods=['POST'])
def capture_order(order_id):
    # 从 PayPal 获取访问令牌
    auth_response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    auth_response.raise_for_status()
    access_token = auth_response.json()["access_token"]

    # 捕获订单
    capture_response = requests.post(
        f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    capture_response.raise_for_status()
    return jsonify(capture_response.json())


@api_bp.route('/api/rag-chat', methods=['POST'])
def api_rag_chat():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({"error": "No query provided", "code": 400}), 400

    chat_response, search_results = rag_chat(query)
    return jsonify({
        "chat_response": chat_response,
        "search_results": search_results,
        "code": 200
    })


@api_bp.route('/conversations', methods=['POST'])
def get_conversations():
    data = request.json
    print("@@@@@@@@")
    user_id = data.get('user_id')
    print(user_id)

    # 查询用户的所有对话,不按时间排序
    conversations = Conversation.query.filter_by(user_id=user_id).all()

    # 将对话和消息转换为字典格式以便于返回
    response = []
    for conversation in conversations[::-1]:  # Reverse the conversations list
        messages = [
            {
                'id': message.id,
                'role': message.role,
                'content': message.content
            } for message in conversation.messages
        ]
        response.append({
            'conversation_id': conversation.id,
            'messages': messages
        })

    return jsonify(response)

# @api_bp.route('/preferences', methods=['POST','GET'])
# def save_preferences():

#     print("Preferences endpoint hit")  # 添加调试信息
#     data = request.json
#     user_id = 1  # 根据您的需求获取动态的用户ID

#     preferences = UserPreferences.query.filter_by(user_id=user_id).first()
#     if not preferences:
#         preferences = UserPreferences(user_id=user_id)

#     preferences.language = data.get('language')
#     preferences.personal_info = data.get('personal_info')
#     preferences.preset_prompts = ','.join(data.get('preset_prompts', []))

#     db.session.add(preferences)
#     db.session.commit()

#     return jsonify(success=True)


@api_bp.route('/preferences', methods=['POST', 'GET'])
def save_preferences():
    print("Preferences endpoint hit")  # 添加调试信息

    if request.method == 'POST':
        data = request.json
        user_id = data.get('userid')  # 从请求体中获取 userid

        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = UserPreferences(user_id=user_id)

        preferences.language = data.get('language')
        preferences.personal_info = data.get('personal_info')
        preferences.preset_prompts = ','.join(data.get('preset_prompts', []))

        db.session.add(preferences)
        db.session.commit()

        return jsonify(success=True)

    elif request.method == 'GET':
        user_id = request.args.get('userid')  # 从查询参数中获取 userid

        preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        if not preferences:
            return jsonify(success=False, message="Preferences not found"), 404

        return jsonify({
            'success': True,
            'language': preferences.language,
            'personal_info': preferences.personal_info,
            'preset_prompts': preferences.preset_prompts.split(',') if preferences.preset_prompts else []
        })


@api_bp.route('/api/rag-chat-my', methods=['POST'])
@token_required
def api_rag_chat_my():
    data = request.json
    query = data.get('query', '')
    web_query = data.get('web_query', '')
    headers = request.headers
    Token = headers.get("X-Token")

    if not query:
        return jsonify({"error": "No query provided", "code": 400}), 400

    email = tk.decode_token(Token)
    insert_sql = "INSERT INTO `session` (email, web_query, query) VALUES ('{}', '{}', '{}');".format(
        email, web_query, query)
    tm.execute_sql(insert_sql, is_query=False)

    chat_response, search_results = rag_chat(query)
    data = {
        "chat_response": chat_response,
        "search_results": search_results
    }
    return jsonify({
        "data": data,
        "code": 200
    })


@api_bp.route("/chat", methods=["GET", "POST"])
def chat_more():
    user_id = None
    if request.method == "POST":
        print("1step")
        data = request.get_json()
        user_id = data.get("userid")
        query = data.get("query")
        history_rounds = data.get("history_rounds", 5)
    elif request.method == "GET":
        print("2step")
        user_id = request.args.get("userid")
        query = request.args.get("query")
        history_rounds = int(request.args.get("history_rounds", 5))

    def generate():
        attempt = 0
        max_attempts = 2
        while attempt < max_attempts:
            try:
                print("检查用户")
                # 检查用户
                user = User.query.filter_by(id=user_id).first()
                if not user:
                    yield "data: " + json.dumps({"error": "User not found"}) + "\n\n"
                    return
                print("this is user", user)
                print("检查用户完成,开始获取用户的历史记录")
                # 获取用户的历史对话
                conversation = Conversation.query.filter_by(
                    user_id=user_id).first()
                if not conversation:
                    conversation = Conversation(user_id=user_id)
                    db.session.add(conversation)
                    db.session.commit()
                # 从历史消息中选择最近的几轮消息
                messages = (
                    Message.query.filter_by(conversation_id=conversation.id)
                    .order_by(Message.id.desc())
                    .limit(history_rounds)
                    .all()
                )
                print("5")
                # 初始化 messagesid
                messagesid = 2
                if messages:
                    messagesid = int(messages[0].id) + 2
                messages = [
                    {"role": msg.role, "content": msg.content} for msg in reversed(messages)
                ]
                print("6")
                # 提炼对话信息
                # context = messages
                context = extract_info_from_conversation(messages)
                print("this is context", context)
                # 获取 GPT 响应生成器
                gpt_response_generator, processed_results, raw_results = rag_chat(
                    query, context)
                full_response = ""
                answer_content = ""
                related_questions_flag = False  # 标记是否进入 Related Questions 部分
                related_questions = []

                yield "data: " + json.dumps({
                    "gpt_content": "Wait a moment...",
                    "related_questions": [],
                    "message_id": messagesid,
                    "raw_results": raw_results,
                    "code": 200
                }) + "\n\n"
                print("开始流式输出")
                # 初始流式输出
                for chunk in gpt_response_generator:
                    full_response += chunk  # 累计完整响应
                    # 去除 `## Answer:` 和 `## Related Questions:` 部分
                    full_response_cleaned = full_response.replace(
                        "## Answer:", "").strip()

                    # 检查是否包含 "## Related Questions" 部分
                    if "## Related Questions:" in full_response_cleaned:
                        related_questions_flag = True
                        answer_content = full_response_cleaned.split(
                            "## Related Questions:")[0].strip()
                        # 提取 Related Questions 部分的每个问题
                        extracted_questions = re.search(
                            r"Related Questions:\s*(.*)", full_response_cleaned, re.S)
                        if extracted_questions:
                            related_questions_str = extracted_questions.group(
                                1).strip()
                            # 将字符串按行分割并去除前后空白
                            related_questions_lines = related_questions_str.splitlines()
                            # 去除每行前面的数字和点号,并过滤掉空行
                            related_questions = [re.sub(r'^\d+\.\s*', '', line.strip())
                                                 for line in related_questions_lines if line.strip()]
                        else:
                            print("未找到指定内容.", full_response_cleaned)
                    else:
                        answer_content = full_response_cleaned
                    # 持续流式输出 answer 部分
                    if not related_questions_flag:
                        yield "data: " + json.dumps({
                            "gpt_content": answer_content.strip(),
                            "related_questions": [],
                            "message_id": messagesid,
                            "raw_results": raw_results,
                            "code": 200
                        }) + "\n\n"
                print("6steps")
                # 最后一次全部发送
                yield "data: " + json.dumps({
                    "gpt_content": answer_content.strip(),
                    "related_questions": related_questions,
                    "message_id": messagesid,
                    "raw_results": raw_results,
                    "code": 200
                }) + "\n\n"

                # 发送 END_OF_STREAM 事件来指示流结束
                yield "data: " + json.dumps({"event": "END_OF_STREAM"}) + "\n\n"

                print("7step")
                # 存储用户提问和GPT回答
                user_message = Message(
                    conversation_id=conversation.id, role="user", content=query)
                gpt_message = Message(
                    conversation_id=conversation.id, role="gpt", content=full_response
                )
                db.session.add(user_message)
                db.session.add(gpt_message)
                db.session.commit()
                # 存储 Related Questions
                if processed_results:
                    for question in processed_results:
                        new_related_question = RelatedQuestion(
                            messages_id=messagesid, question=question['link'])
                        db.session.add(new_related_question)
                    db.session.commit()
                break  # 成功执行后退出循环
            except Exception as e:
                db.session.rollback()
                print(f"Error occurred: {e}")  # 调试异常
                print("_______________")
                yield "data: " + json.dumps({"error": "An error occurred while processing the chat", "code": 500}) + "\n\n"
                attempt += 1
                if attempt >= max_attempts:
                    yield "data: " + json.dumps({"error": "Max attempts reached", "code": 500}) + "\n\n"

    # 确保返回 Response 对象
    print("Returning Response object")
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


# @api_bp.route("/chat", methods=["POST","GET"])
# def chat_more():
#     data = request.get_json()
#     user_id = data.get("userid")
#     query = data.get("query")
#     history_rounds = data.get("history_rounds", 5)  # 可调整的历史对话轮数

#     # 检查用户
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     # 获取用户的历史对话
#     conversation = Conversation.query.filter_by(user_id=user_id).first()
#     if not conversation:
#         conversation = Conversation(user_id=user_id)
#         db.session.add(conversation)
#         db.session.commit()

#     # 从历史消息中选择最近的几轮消息
#     messages = (
#         Message.query.filter_by(conversation_id=conversation.id)
#         .order_by(Message.id.desc())
#         .limit(history_rounds)
#         .all()
#     )
#     messages = [
#         {"role": msg.role, "content": msg.content} for msg in reversed(messages)
#     ]
#     print(messages)
#     # 提炼对话信息
#     context = messages

#     # 调用GPT获取回答
#     gpt_response = chat_with_mygpt(query, context)
#     print(gpt_response)

#     # 使用正则表达式提取从 ## Answer: 到 [result:5]. 之间的内容
#     extracted_content = re.search(r"## Answer:(.*?)## Related Questions:", gpt_response, re.S)
#     if extracted_content:
#         gpt_content = extracted_content.group(1).strip()
#     else:
#         gpt_content = gpt_response  # 如果没有匹配,保留完整回答
#     print(gpt_content)
#     # # 提取 Related Questions 部分的每个问题
#     # extracted_questions = re.search(r"## Related Questions:\s*(.*)", gpt_response, re.S)
#     # if extracted_questions:
#     #     related_questions_str = extracted_questions.group(1).strip()
#     #     related_questions = [question.strip() for question in related_questions_str.split('\n') if question.strip()]
#     #     print(related_questions)
#     # else:
#     #     print("未找到指定内容.")


#     # 提取 Related Questions 部分的每个问题
#     extracted_questions = re.search(r"## Related Questions:\s*(.+)", gpt_response, re.DOTALL)
#     if extracted_questions:
#         # 使用 splitlines 方法逐行分割,去除每行多余的空白
#         related_questions_str = extracted_questions.group(1).strip()
#         related_questions = [
#             line.strip() for line in related_questions_str.splitlines() if line.strip()  # 去掉空行
#         ]
#         print(related_questions)  # 输出结果为数组形式
#     else:
#         print("未找到指定内容.")

#     # 存储用户提问和GPT回答
#     user_message = Message(conversation_id=conversation.id, role="user", content=query)
#     gpt_message = Message(
#         conversation_id=conversation.id, role="gpt", content=gpt_content
#     )
#     db.session.add(user_message)
#     db.session.add(gpt_message)
#     db.session.commit()

#     return jsonify({
#         "gpt_content": gpt_content,
#         "related_questions": related_questions,
#         "code": 200
#     })


@api_bp.route('/test', methods=['POST'])
@token_required
def api_rag_chattest():
    data = {
        "chat_response": 1,
        "search_results": 1
    }
    return jsonify({
        "code": 200,
        "data": data
    })


@api_bp.route('/analyze-event', methods=['POST'])
def api_analyze_event():
    try:
        logger.info("=== Received analyze-event request ===")
        data = request.json
        event_description = data.get('event_description')
        logger.info(f"Event description: {event_description}")

        if not event_description:
            logger.error("Empty event description")
            return jsonify({
                "code": 400,
                "message": "Event description is required"
            }), 400

        def generate():
            current_question = None
            current_answer = ""
            
            try:
                for result in analyze_event(event_description):
                    if result["type"] == "initial_context":
                        yield f"data: {json.dumps({'type': 'initial_context', 'content': result['content']})}\n\n"
                    
                    elif result["type"] == "processing":
                        yield f"data: {json.dumps({'type': 'processing', 'content': result['content']})}\n\n"
                    
                    elif result["type"] == "answer":
                        if current_question != result["question_number"]:
                            if current_question is not None:
                                # 输出上一个问题的完整答案
                                yield f"data: {json.dumps({'type': 'complete', 'question_number': current_question, 'content': current_answer})}\n\n"
                            current_question = result["question_number"]
                            current_answer = ""
                        current_answer += result["content"]
                        yield f"data: {json.dumps({'type': 'answer', 'question_number': result['question_number'], 'content': result['content']})}\n\n"
                    
                    elif result["type"] == "complete":
                        current_question = None
                        current_answer = ""
                        yield f"data: {json.dumps({'type': 'complete', 'question_number': result['question_number'], 'content': result['content']})}\n\n"
                    
                    elif result["type"] == "search_results":
                        yield f"data: {json.dumps({'type': 'search_results', 'content': result['content']})}\n\n"
                    
                    elif result["type"] == "error":
                        yield f"data: {json.dumps({'type': 'error', 'content': result['content']})}\n\n"
                
                # 发送结束标记
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in generate: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Internal server error: {str(e)}"
        }), 500


@api_bp.route('/publish-tweet', methods=['POST'])
def publish_tweet():
    """分析事件并发布单条推文"""
    try:
        data = request.json
        event_description = data.get('event_description')

        if not event_description:
            return jsonify({
                "code": 400,
                "error": "事件描述不能为空",
                "message": "Event description cannot be empty"
            }), 400

        try:
            # 调用事件分析函数
            analysis_result = analyze_event(event_description)
            if not analysis_result:
                return jsonify({
                    "code": 500,
                    "error": "事件分析失败,未能获取结果",
                    "message": "Failed to get analysis result"
                }), 500

            # 初始化推特发布器
            twitter = TwitterPublisher()

            # 发布单条推文
            published_tweet = twitter.publish_single_tweet(analysis_result)

            if not published_tweet:
                return jsonify({
                    "code": 500,
                    "error": "推文发布失败",
                    "message": "Failed to publish tweet"
                }), 500

            return jsonify({
                "code": 200,
                "data": {
                    "analysis": analysis_result,
                    "published_tweet": published_tweet
                },
                "message": "Successfully published to Twitter"
            })

        except ConnectionError as conn_error:
            logging.error(f"Connection error: {str(conn_error)}")
            return jsonify({
                "code": 500,
                "error": "网络连接错误,请检查网络并重试",
                "detail": str(conn_error),
                "message": "Network connection error"
            }), 500

        except Exception as analysis_error:
            logging.error(f"Event analysis or Twitter publishing error: {str(analysis_error)}")
            return jsonify({
                "code": 500,
                "error": "处理过程中发生错误,请稍后重试",
                "detail": str(analysis_error),
                "message": "Error occurred during processing"
            }), 500

    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({
            "code": 500,
            "error": "服务器内部错误",
            "detail": str(e),
            "message": "Internal server error"
        }), 500

# 在run.py中注册蓝图
# app.register_blueprint(api_bp, url_prefix='/api')
