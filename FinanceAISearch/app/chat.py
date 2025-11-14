import json  # Add this import statement
import logging
from app.search import serper_search, process_search_results
from app.config import Config
import openai
import sys
import os
from app.models import User, Conversation, Message, RelatedQuestion, db
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config = Config()
openai.api_key = config.OPENAI_API_KEY


logger = logging.getLogger(__name__)
config = Config()
openai.api_key = ""
# openai.api_key = ""
# print(api_key)
# openai.api_key
# client = OpenAI(api_key=api_key)
# client = OpenAI(
#     api_key="",
#     base_url="https://api.deepseek.com/v1",
# )



def extract_info_from_conversation(messages):
    """调用信息提炼的API,提取关键内容"""
    context_text = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in messages])
    prompt = f"""请从以下对话中提取关键信息:
    {context_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that distills conversation history for brevity and relevance.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def chat_with_mygpt(query, context):
    prompt = f"""You are an advanced AI assistant specializing in finance and technology, created by a leading AI company. Your task is to provide detailed, thoughtful, and insightful answers to user queries based on the given search results. Please follow these guidelines:

        1. Each search result is prefixed with a reference number like [[result:x]], where x is a number. Use these to cite your sources.

        2. Provide accurate and expert-level responses using an unbiased and professional tone.

        3. Cite the search results at the end of each relevant sentence using the format <sup>x</sup>, where x is the reference number. For example, if information comes from multiple results, list all applicable citations, e.g., <sup>3,5</sup>. Ensure that each citation corresponds to the reference provided at the end of the document.

        4. Ensure your answers are comprehensive, including in-depth analysis, market implications, and potential opportunities or risks related to the topic.

        5. Where applicable, assess both short-term and long-term impacts on the investment market, considering factors such as macroeconomic trends, industry shifts, and investor sentiment.

        6. Highlight any potential uncertainties or areas of volatility that could affect the market outcome.

        7. If the search results don't provide sufficient information on a relevant topic, state "Information is missing on [topic]".

        8. Other than specific terms, names, or citations, your answer should be in the same language as the user's question.

        9. Do not quote the search results verbatim. Synthesize the information to provide a coherent and engaging answer.

        10. When asked about recent events or current data, remind the user that the information is based on the search results and may not be up to date.

        Here are the search results:
        {context}

        Please answer the following user question:
        {query}

        ---
        After answering the question, provide 5 related questions that the user might also be interested in, based on the user question and search results. Ensure these questions explore broader or deeper aspects of the topic, including its implications for various stakeholders.

        ## Answer:
        [Your synthesized answer here, including detailed analysis and implications for the investment market.]

        ## Related Questions:
        1. [First related question]
        2. [Second related question]
        3. [Third related question]
        ...
        """
    # 流式返回 GPT 响应
    # # 获取用户的历史对话
    # conversation = Conversation.query.filter_by(user_id=user_id).first()
    # if not conversation:
    #     conversation = Conversation(user_id=user_id)
    #     db.session.add(conversation)
    #     db.session.commit()
    #     # 从历史消息中选择最近的几轮消息
    #     messages = (
    #                 Message.query.filter_by(conversation_id=conversation.id)
    #                 .order_by(Message.id.desc())
    #                 .limit(history_rounds)
    #                 .all()
    #             )
    print("5")
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided search results and generates related questions."},

            {"role": "user", "content": prompt},
        ],
        stream=True
    )
    print("this is response", response)
    full_response = ""
    try:
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    content = delta['content']
                    print(content)
                    yield content
                    full_response += content
                elif 'role' in delta:
                    print(f"Role change detected: {delta['role']}")
                # Handle other possible keys in delta if needed
                else:
                    print(f"Unhandled delta: {delta}")
            else:
                print("Received empty chunk or no choices:", chunk)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        response.close()
        print("Response stream closed.")


def parse_gpt_answer_questions(output_text):
    # Define regular expressions to extract the answer and related questions
    answer_pattern = r"## Answer:\n([\s\S]*?)\n## Related Questions:"
    related_questions_pattern = r"## Related Questions:\n([\s\S]*)"

    # Search for the answer using the pattern
    answer_match = re.search(answer_pattern, output_text)
    answer = answer_match.group(1).strip(
    ) if answer_match else "No answer found."

    # Search for the related questions using the pattern
    related_questions_match = re.search(related_questions_pattern, output_text)
    related_questions_text = related_questions_match.group(
        1).strip() if related_questions_match else "No related questions found."

    # Split the related questions into a list
    related_questions = [q.strip()
                         for q in related_questions_text.split('\n') if q]

    # Return the parsed result as a dictionary
    return {
        "answer": answer,
        "related_questions": related_questions
    }


def generate_context(search_results):
    context = ""
    for result in search_results:
        context += f"Title: {result.get('title', 'No Title')}\nSnippet: {result.get('snippet', 'No Snippet')}\n\n"
    return context


def chat_with_gpt(query, context):
    prompt = f"""You are an advanced AI assistant specializing in finance and technology, created by a leading AI company. Your task is to provide detailed, thoughtful, and insightful answers to user queries based on the given search results. Please follow these guidelines:

        1. Each search result is prefixed with a reference number like [[result:x]], where x is a number. Use these to cite your sources.

        2. Provide accurate and expert-level responses using an unbiased and professional tone.

        3. Cite the search results at the end of each relevant sentence using the format [result:x]. If information comes from multiple results, list all applicable citations, e.g., [result:3][result:5].

        4. Ensure your answers are comprehensive, including in-depth analysis, market implications, and potential opportunities or risks related to the topic.

        5. Where applicable, assess both short-term and long-term impacts on the investment market, considering factors such as macroeconomic trends, industry shifts, and investor sentiment.

        6. Highlight any potential uncertainties or areas of volatility that could affect the market outcome.

        7. If the search results don't provide sufficient information on a relevant topic, state "Information is missing on [topic]".

        8. Other than specific terms, names, or citations, your answer should be in the same language as the user's question.

        9. Do not quote the search results verbatim. Synthesize the information to provide a coherent and engaging answer.

        10. When asked about recent events or current data, remind the user that the information is based on the search results and may not be up to date.

        Here are the search results:
        {context}

        Please answer the following user question:
        {query}

        ---
        After answering the question, provide 5-10 related questions that the user might also be interested in, based on the user question and search results. Ensure these questions explore broader or deeper aspects of the topic, including its implications for various stakeholders.

        ## Answer:
        [Your synthesized answer here, including detailed analysis and implications for the investment market.]

        ## Related Questions:
        1. [First related question]
        2. [Second related question]
        3. [Third related question]
        ...
        """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided search results and generates related questions."},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    # 流式返回 GPT 响应
    for chunk in response:
        if 'choices' in chunk and len(chunk['choices']) > 0:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                content = delta['content']
                print(content)
                yield content
        else:
            print("Received empty chunk or no content:", chunk)


def rag_chat(query, context):
    print("hello rag_chat")
    """
    Perform a RAG (Retrieval-Augmented Generation) chat by first searching for information
    and then using the search results to inform the chat response.
    
    :param query: The user's query string
    :param context: Additional context for the chat
    :return: A tuple containing the chat response generator and the search results
    """
    try:
        # Step 1: Perform the search
        raw_results = serper_search(query)
        if isinstance(raw_results, list) and len(raw_results) > 0 and isinstance(raw_results[0], str) and raw_results[0].startswith('Error:'):
            logger.error(f"Search failed: {raw_results[0]}")
            # 即使搜索失败，也继续使用现有上下文生成回答
            processed_results = []
            search_context = context
        else:
            processed_results = process_search_results(raw_results)
            # Step 2: Generate context from search results
            search_context = generate_context(processed_results)
            if context:
                search_context = f"{context}\n\n{search_context}"
        
        # Step 3: Get chat response generator
        chat_response = chat_with_mygpt(query, search_context)
        
        return chat_response, processed_results, raw_results
        
    except Exception as e:
        logger.error(f"Error in rag_chat: {str(e)}")
        # 返回一个基于现有上下文的回答生成器
        chat_response = chat_with_mygpt(query, context or "")
        return chat_response, [], []


def extract_information(text):
    extraction_prompt = f"""Based on the following text, please extract and list:
    1. Related events (including their dates or time periods and contexts)
    2. Related stocks or companies
    3. Related concepts or technologies

    For each category, provide the items as a comma-separated list. If there are no items for a category, return an empty list.

    Text to analyze:
    {text}

    Format your response as follows:
    Events: [list of events]
    Stocks: [list of stocks or companies]
    Concepts: [list of concepts or technologies]
    """

    extraction_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts specific information from text."},
            {"role": "user", "content": extraction_prompt}
        ]
    )

    extraction_result = extraction_response.choices[0].message.content

    # 解析提取结果
    related_events = []
    related_stocks = []
    related_concepts = []

    for line in extraction_result.split('\n'):
        if line.startswith('Events:'):
            related_events = [event.strip() for event in line[7:].strip(
                '[]').split(',') if event.strip()]
        elif line.startswith('Stocks:'):
            related_stocks = [stock.strip() for stock in line[7:].strip(
                '[]').split(',') if stock.strip()]
        elif line.startswith('Concepts:'):
            related_concepts = [concept.strip() for concept in line[9:].strip(
                '[]').split(',') if concept.strip()]

    return related_events, related_stocks, related_concepts


def extract_information_detailed(text):
    extraction_prompt = f"""Based on the following text, please extract and provide detailed information on:
    1. Related events: Include the event name, date or time period, a brief description, and its significance or impact. Provide as much context as possible.
    2. Related stocks or companies: List the company names or stock symbols, and briefly explain their relevance to the topic.
    3. Related concepts or technologies: List the concepts or technologies, and provide a short explanation of how they relate to the main topic.

    For each category, provide the items as a numbered list. If there are no items for a category, state that no relevant items were found.

    Text to analyze:
    {text}

    Format your response as follows:
    Events:
    1. [Event name]: [Date/Period] - [Detailed description including context, significance, and impact]
    2. ...

    Stocks/Companies:
    1. [Company name/Stock symbol]: [Brief explanation of relevance]
    2. ...

    Concepts/Technologies:
    1. [Concept/Technology name]: [Explanation of relation to the topic]
    2. ...
    """

    extraction_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts and elaborates on specific information from text."},
            {"role": "user", "content": extraction_prompt}
        ]
    )

    extraction_result = extraction_response.choices[0].message.content
    # 使用正则表达式提取各部分
    events_match = re.search(
        r'Events:(.*?)(?:Stocks/Companies:|Concepts/Technologies:|$)', extraction_result, re.DOTALL)
    stocks_match = re.search(
        r'Stocks/Companies:(.*?)(?:Events:|Concepts/Technologies:|$)', extraction_result, re.DOTALL)
    concepts_match = re.search(
        r'Concepts/Technologies:(.*?)(?:Events:|Stocks/Companies:|$)', extraction_result, re.DOTALL)

    def extract_items(text):
        if text:
            # 使用正则表达式匹配编号项
            items = re.findall(r'^\s*\d+\.\s*(.*?)(?=^\s*\d+\.|\Z)',
                               text.strip(), re.MULTILINE | re.DOTALL)
            return [item.strip() for item in items if item.strip()]
        return []

    related_events = extract_items(
        events_match.group(1) if events_match else "")
    related_stocks = extract_items(
        stocks_match.group(1) if stocks_match else "")
    related_concepts = extract_items(
        concepts_match.group(1) if concepts_match else "")
    return related_events, related_stocks, related_concepts


def analyze_event(event_description):
    """分析事件相关的投资市场机会,包括受影响的股票"""
    # 首先搜索事件的最新信息
    event_context = rag_chat(event_description)

    sub_questions = [
        "1. 事件概述: 请简要描述这个事件的主要内容和关键点.",
        "2. 市场影响: 这个事件如何影响相关产业的市场格局?",
        "3. 投资热点: 围绕这个事件,可能出现哪些新的投资热点或趋势?",
        "4. 潜在风险: 投资者需要注意哪些潜在的风险或挑战?",
        "5. 受益股票: 哪些具体的上市公司(包括股票代码)可能从这个事件中直接受益?为什么?",
        "6. 间接受益股票: 哪些相关产业链的上市公司(包括股票代码)可能间接受益?",
        "7. 可能受损股票: 有哪些公司(包括股票代码)可能因此受到负面影响?",
        "8. 行业展望: 这个事件对相关行业的长期发展有何启示?",
        "9. 国际投资机会: 这个事件是否为国际投资者带来了新的投资机会?",
        "10. 政策影响: 相关的政策环境可能如何变化,会对投资产生什么影响?",
        "11. 投资策略: 基于这个事件,投资者应该如何调整其投资组合?"
    ]

    answers = {}
    for question in sub_questions:
        question_number = question.split(".")[0]
        question_content = question.split(":")[1].strip()


        query = f"{event_description}\n\n{event_context}\n\n考虑投资市场的机会,特别是可能受影响的股票,{question_content}"

        answer, _ = rag_chat(query)

        answers[question_number] = answer.strip()

    # 编制初步分析报告
    initial_report = f"事件投资机会及股票影响分析报告:\n\n最新事件信息:\n{event_context}\n分析结果:\n"
    for i in range(1, len(sub_questions) + 1):
        question_number = str(i)
        initial_report += f"\n{sub_questions[i-1]}\n"
        initial_report += answers.get(question_number, "未能获取回答.") + "\n"

    # 使用 chat_with_gpt 生成最终报告
    final_report_query = f"""
    基于以下关于该事件的初步分析报告,请生成一份简洁、全面且结构良好的投资机会分析报告.
    报告应该重点关注该事件带来的投资市场机会,尤其要详细分析可能受影响的具体股票.请包括以下内容:

    1. 事件概述
    2. 市场影响和新兴投资热点
    3. 直接受益的股票(请列出具体公司名称和股票代码)
    4. 间接受益的相关产业链股票
    5. 可能受到负面影响的股票
    6. 潜在风险和挑战
    7. 行业长期发展展望
    8. 国际投资者的机会
    9. 政策环境变化对投资的影响
    10. 针对相关股票的具体投资策略建议

    请确保报告逻辑清晰,重点突出,并提供对潜在投资者有实际价值的见解和建议.对于提到的每只股票,请尽可能提供其股票代码和简要分析.

    初步分析报告:
    {initial_report}
    """

    final_report = chat_with_gpt(final_report_query, "")

    return final_report.strip()


def get_financial_hotspots(limit=20):
    """
    使用搜索引擎获取当前的金融热点事件.

    :param limit: 初始获取的热点事件数量(后续会进行筛选)
    :return: 包含热点事件的列表
    """
    queries = [
        "今日金融要闻",
        "实时财经热点",
        "最新经济新闻",
        "股市重要公告",
        "今日财经头条"
    ]

    all_results = []
    for query in queries:
        raw_results = serper_search(query)
        processed_results = process_search_results(raw_results)
        all_results.extend(processed_results)

    # 去重,防止不同查询返回相同的新闻
    unique_results = {result['title']
        : result for result in all_results}.values()

    # 选取前 limit 条结果
    top_results = list(unique_results)[:limit]

    hotspots = []
    for result in top_results:
        hotspot = {
            'title': result['title'],
            'description': result['snippet'],
            'url': result['link']
        }
        hotspots.append(hotspot)

    return hotspots


def select_top_hotspots(hotspots, top_n=10):
    """
    使用模型选择最重要的热点事件.

    :param hotspots: 原始热点事件列表
    :param top_n: 需要选择的热点事件数量
    :return: 最重要的热点事件列表
    """
    # 将所有热点事件转换为一个字符串
    hotspots_text = "\n\n".join(
        [f"标题:{h['title']}\n描述:{h['description']}" for h in hotspots])

    prompt = f"""
    以下是一系列金融热点事件.请从中选择最重要的{top_n}条,并按重要性从高到低排序.
    在选择时,请考虑以下因素:
    1. 事件对金融市场的潜在影响
    2. 事件的规模和范围
    3. 事件的新颖性和时效性
    4. 事件涉及的主体的重要性(如大型企业、国家政策等)

    请以下面的格式列出选中的事件:
    1. [事件标题]
    2. [事件标题]
    ...

    热点事件列表:
    {hotspots_text}
    """

    response, _ = rag_chat(prompt)

    # 解析模型的响应
    selected_titles = [line.split('. ', 1)[1].strip() for line in response.split(
        '\n') if line.strip() and line[0].isdigit()]

    # 根据选中的标题筛选原始热点事件
    selected_hotspots = [h for h in hotspots if h['title'] in selected_titles]

    # 确保顺序与模型给出的顺序一致
    ordered_hotspots = []
    for title in selected_titles:
        for hotspot in selected_hotspots:
            if hotspot['title'] == title:
                ordered_hotspots.append(hotspot)
                break

    return ordered_hotspots


def enrich_hotspots(hotspots):
    """
    使用 GPT 模型丰富热点事件的描述和上下文.

    :param hotspots: 原始热点事件列表
    :return: 丰富后的热点事件列表
    """
    enriched_hotspots = []
    for hotspot in hotspots:
        prompt = f"""
        基于以下金融热点事件的标题和描述,生成一个简洁的事件描述(不超过50个字)
        和一个详细的上下文信息(不超过200个字):

        标题:{hotspot['title']}
        原始描述:{hotspot['description']}

        请按以下格式输出:
        事件描述:[简洁描述]
        上下文:[详细上下文]
        """
        response, _ = rag_chat(prompt)

        # 解析 GPT 的响应
        lines = response.strip().split('\n')
        enriched_hotspot = {
            'title': hotspot['title'],
            'event_description': lines[0].replace('事件描述:', '').strip() if len(lines) > 0 else '',
            'context': lines[1].replace('上下文:', '').strip() if len(lines) > 1 else '',
            'url': hotspot['url']
        }
        enriched_hotspots.append(enriched_hotspot)

    return enriched_hotspots


if __name__ == '__main__':
    answer, results = rag_chat("apple 股票走势分析")
    print(answer)
    res = parse_gpt_answer_questions(answer)
    print(res)
    # # 获取原始热点事件(获取较多的事件,以便后续筛选)
    # raw_hotspots = get_financial_hotspots(20)

    # # 使用模型选择最重要的10条热点事件
    # top_hotspots = select_top_hotspots(raw_hotspots, 10)

    # # 使用 GPT 丰富热点事件的描述
    # enriched_hotspots = enrich_hotspots(top_hotspots)

    # print("Today's Top 10 Financial Hotspots and Analysis:")
    # for index, hotspot in enumerate(enriched_hotspots, 1):
    #     print(f"\n{index}. {hotspot['title']}")
    #     print(f"Event Description: {hotspot['event_description']}")
    #     print(f"Context: {hotspot['context']}")
    #     print(f"Source URL: {hotspot['url']}")
    #     print("Analyzing event...")
    #     analysis = analyze_event(f"{hotspot['event_description']}\n\n{hotspot['context']}")
    #     print("Event Analysis:")
    #     print(analysis)
    #     print("---")
