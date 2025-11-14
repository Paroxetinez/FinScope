import openai
import os
openai.api_key = ""

def chat_with_mygpt(query, context):
    prompt = f"""You are an advanced AI assistant specializing in finance and technology, created by a leading AI company. Your task is to provide clear, concise, and accurate answers to user queries based on the given search results. Please follow these guidelines:
    
        2. Provide accurate and expert-level responses using an unbiased and professional tone. 

        4. Limit your response to approximately 1024 tokens.

        5. Only provide information directly related to the question. Avoid repetition.

        6. If the search results don't provide sufficient information on a relevant topic, state "Information is missing on [topic]".

        7. Other than specific terms, names, or citations, your answer should be in the same language as the user's question.

        8. Do not quote the search results verbatim. Synthesize the information to provide a coherent answer.

        9. If asked about recent events or current data, remind the user that the information is based on the search results and may not be up to date.

        Here are the search results:
        {context}

        Please answer the following user question:
        {query}

        ---
        After answering the question, provide 5-10 related questions that the user might also be interested in, based on the user question and search results.
        Do not include any numbering or bullets, just a plain list of questions in natural language format.
        Please use this structured format:

        ## Answer:
        [Your synthesized answer here.]

        ## Related Questions:
        [First related question]
        [Second related question]
        [Third related question]
        ...
        """
        
    #在这里提炼历史记录，放到多轮对话里 
    
    # 流式返回 GPT 响应
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if 'choices' in chunk and len(chunk['choices']) > 0:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                content = delta['content']
                print(content)
                yield content
        else:
            print("Received empty chunk or no content:", chunk)

query = "nihao"
context = "666"

gpt_response_generator = chat_with_mygpt(query, context)

full_response = ""  # 用于拼接完整的响应
print(gpt_response_generator)
for chunk in gpt_response_generator:
    full_response += chunk  # 拼接当前的 chunk 内容
    print(chunk)  # 打印调试信息

    # 每次返回拼接后的内容
    # yield "data: " + json.dumps({
    #     "gpt_content": full_response,  # 返回当前的拼接内容
    #     "related_questions": [],  # 相关问题可以根据需求填写
    #     "message_id": "some_message_id",  # 你可以动态生成 message_id
    #     "code": 200
    # }) + "\n\n"