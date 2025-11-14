import openai
import sys
import os
import time
import enum
from typing import Dict, List, Tuple, Optional, Generator, Union
import logging

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from FinanceAISearch.app.chat import rag_chat
    from FinanceAISearch.app.search import serper_search, process_search_results
    from FinanceAISearch.app.config import Config
except ImportError:
    from app.chat import rag_chat
    from app.search import serper_search, process_search_results
    from app.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

config = Config()
openai.api_key = config.OPENAI_API_KEY

class AnalysisError(enum.Enum):
    API_ERROR = "API Error"
    TIMEOUT = "Request Timeout"
    CONTENT_ERROR = "Content Processing Error"
    UNKNOWN = "Unknown Error"

class RetryStrategy:
    """Retry strategy for API calls"""
    MAX_RETRIES = 3
    BASE_DELAY = 1  # 基础延迟时间（秒）
    
    @staticmethod
    def get_delay(retry_count: int) -> float:
        """Calculate delay for retry attempt"""
        return RetryStrategy.BASE_DELAY * (2 ** retry_count)  # 指数退避

def format_error_message(error_type: AnalysisError, details: str = "") -> str:
    """Format error message in English"""
    base_message = f"Analysis encountered {error_type.value}"
    if details:
        return f"{base_message}: {details}"
    return base_message

def create_analysis_prompt(event_description: str, question: str, context: str) -> str:
    """Create analysis prompt in English"""
    return f"""Please analyze the following event from an investment perspective:

Event Description: {event_description}

Background Information:
{context}

Analysis Question: {question}

Please provide a comprehensive analysis focusing on:
1. Market Impact
   - Short-term market reactions
   - Long-term market implications
   - Industry-wide effects

2. Stock Analysis
   - Direct beneficiary stocks
   - Potentially affected companies
   - Market performance indicators

3. Investment Opportunities
   - Emerging opportunities
   - Sector-specific prospects
   - Strategic positioning

4. Risk Assessment
   - Market risks
   - Regulatory concerns
   - Competitive challenges

Please provide detailed analysis with specific examples and data where possible.
Focus on actionable insights for investors.
"""

def collect_generator_output(generator) -> str:
    """
    Collect output from generator or handle string directly.
    """
    try:
        if isinstance(generator, str):
            return generator
        
        result = []
        for chunk in generator:
            if chunk:
                result.append(str(chunk))
        return "".join(result)
    except Exception as e:
        logger.error(f"Error in collect_generator_output: {str(e)}")
        return ""

def split_question(question_text: str) -> Tuple[str, str]:
    """
    Split question text into number and content.
    
    Args:
        question_text: The question text to split
        
    Returns:
        Tuple[str, str]: Question number and content
    """
    try:
        number_parts = question_text.split(".")
        question_number = number_parts[0].strip() if len(number_parts) > 1 else "0"
        
        # Try English colon first
        parts = question_text.split(":")
        if len(parts) > 1:
            return question_number, parts[1].strip()

        return question_number, question_text.strip()
    except Exception as e:
        logger.error(f"Failed to split question text: {str(e)}")
        return "0", question_text.strip()

def handle_rag_chat_response(response, context: str = "", default_message: str = "") -> Tuple[str, List, List]:
    """
    Handle different types of responses from rag_chat
    
    Args:
        response: The response from rag_chat
        context: Current context for fallback
        default_message: Default message if no context available
        
    Returns:
        Tuple[str, List, List]: Processed response, processed results, and raw results
    """
    # 如果响应是列表且只包含错误信息
    if isinstance(response, list) and len(response) == 1 and isinstance(response[0], str) and response[0].startswith('Error:'):
        logger.warning(f"Received error response from rag_chat: {response[0]}")
        # 返回基于上下文的响应和空结果列表
        return context or default_message, [], []
        
    # 如果响应是字符串
    if isinstance(response, str):
        if response.startswith('Error:'):
            logger.warning(f"Received error string from rag_chat: {response}")
            return context or default_message, [], []
        return response, [], []
        
    # 如果响应是元组
    if isinstance(response, tuple) and len(response) == 3:
        chat_response, processed_results, raw_results = response
        
        # 处理 chat_response
        if isinstance(chat_response, str):
            final_response = chat_response
        else:
            try:
                final_response = collect_generator_output(chat_response)
            except Exception as e:
                logger.error(f"Error collecting generator output: {str(e)}")
                final_response = context or default_message
                
        return final_response, processed_results or [], raw_results or []
        
    # 未知响应类型
    logger.error(f"Unexpected response type from rag_chat: {type(response)}")
    return context or default_message, [], []

def analyze_event(event_description: str) -> Generator:
    """
    Analyze event for investment opportunities with streaming output
    
    Args:
        event_description: Event to analyze
        
    Yields:
        Dict: Contains partial analysis results and search results
    """
    logger.info(f"Starting analysis for event: {event_description}")
    
    all_search_results = []
    
    # 获取初始上下文
    try:
        logger.info("Getting initial context...")
        initial_query = f"Please provide a brief overview of the following event: {event_description}"
        
        # 第一次调用 rag_chat 获取事件概述
        chat_response_generator, processed_results, raw_results = rag_chat(initial_query, "")
        
        # 收集生成器输出
        context = ""
        try:
            for chunk in chat_response_generator:
                if chunk:
                    context += chunk
                    # 实时输出初始概述
                    yield {
                        "type": "initial_context",
                        "content": chunk
                    }
        except Exception as e:
            logger.error(f"Error collecting initial context: {str(e)}")
            context = event_description
            yield {
                "type": "error",
                "content": "Error collecting initial context"
            }
            
        # 处理搜索结果
        if raw_results and isinstance(raw_results, list):
            try:
                valid_results = [r for r in raw_results if isinstance(r, dict) and r.get('link')]
                all_search_results.extend(valid_results)
            except Exception as e:
                logger.error(f"Error processing initial search results: {str(e)}")
                
        logger.info(f"Initial context: {context[:200]}...")
                
    except Exception as e:
        logger.error(f"Failed to get initial context: {str(e)}")
        context = event_description
        yield {
            "type": "error",
            "content": "Failed to get initial context"
        }
    
    # 定义分析问题
    sub_questions = [
        "1. Event Overview: What is the event? When and where did it occur?",
        "2. Direct Impact: Which industries or sectors are directly affected? Is the impact positive or negative?",
        "3. Stakeholder Analysis: Who are the key stakeholders and what roles do they play?",
        "4. Market Response: How has the market initially reacted? What is the consumer and public sentiment?",
        "5. Competitive Landscape: How might competitors respond? What market share changes are likely?",
        "6. Regulatory Impact: Are there new policies or regulations involved? How might the regulatory environment change?",
        "7. Economic Impact: What are the macroeconomic implications? Will it affect economic indicators?",
        "8. Technology & Innovation: What new technologies or innovations are involved? What are their long-term implications?",
        "9. Risk Assessment: What are the potential risks and uncertainties? What is their likelihood and potential impact?",
        "10. Investment Opportunities: Based on the analysis, what investment opportunities exist? Which assets might benefit?",
        "11. Future Outlook: What long-term trends might emerge? How might the industry or market evolve?",
        "12. Strategic Recommendations: What actions or strategies should be taken? What key indicators should be monitored?"
    ]
    
    # 处理每个问题
    for question in sub_questions:
        question_number, question_content = split_question(question)
        logger.info(f"Processing question {question_number}: {question_content[:50]}...")
        
        # 输出当前正在处理的问题
        yield {
            "type": "processing",
            "content": f"Processing: {question_content}"
        }
        
        retry_count = 0
        while retry_count < RetryStrategy.MAX_RETRIES:
            try:
                # 构建分析提示
                prompt = f"""Based on the following event and context, please provide a detailed analysis focusing on the specific aspect mentioned in the question. 
                
                Event Description: {event_description}
                
                Current Context: {context}
                
                Question: {question_content}
                
                Please provide a comprehensive answer that includes specific details, examples, and implications for investors when applicable."""
                
                # 调用 rag_chat 获取答案
                chat_response_generator, processed_results, raw_results = rag_chat(prompt, context)

                # 收集生成器输出
                answer = ""
                try:
                    for chunk in chat_response_generator:
                        if chunk:
                            answer += chunk
                            # 实时输出答案片段
                            yield {
                                "type": "answer",
                                "question_number": question_number,
                                "content": chunk
                            }
                except Exception as e:
                    logger.error(f"Error collecting answer for question {question_number}: {str(e)}")
                    yield {
                        "type": "error",
                        "content": f"Error collecting answer for question {question_number}"
                    }
                    raise Exception(f"Failed to collect answer: {str(e)}")
                
                # 处理搜索结果
                if raw_results and isinstance(raw_results, list):
                    try:
                        valid_results = [r for r in raw_results if isinstance(r, dict) and r.get('link')]
                        all_search_results.extend(valid_results)
                    except Exception as e:
                        logger.error(f"Error processing search results: {str(e)}")

                if answer and len(answer.strip()) > 0:
                    # 输出完整答案
                    yield {
                        "type": "complete",
                        "question_number": question_number,
                        "content": answer.strip()
                    }
                    break
                else:
                    raise Exception("Empty answer received")

            except Exception as e:
                logger.error(f"Failed to process question {question_number}: {str(e)}")
                retry_count += 1
                
                if retry_count >= RetryStrategy.MAX_RETRIES:
                    error_message = "An error occurred while processing this question."
                    yield {
                        "type": "error",
                        "question_number": question_number,
                        "content": error_message
                    }
                else:
                    delay = RetryStrategy.get_delay(retry_count)
                    logger.info(f"Retrying question {question_number} (Attempt {retry_count + 1}/{RetryStrategy.MAX_RETRIES}, delay {delay}s)")
                    time.sleep(delay)
    
    # 处理搜索结果
    logger.info("Processing search results...")
    unique_search_results = []
    seen_links = set()
    
    for result in all_search_results:
        if result.get('link') not in seen_links:
            seen_links.add(result.get('link'))
            unique_search_results.append(result)
    
    logger.info(f"Analysis complete. Found {len(unique_search_results)} unique search results.")
    
    # 输出最终的搜索结果
    yield {
        "type": "search_results",
        "content": unique_search_results[:10]  # 限制返回前10个结果
    }

if __name__ == '__main__':
    event_description = "<黑神话:悟空>爆火,引起广泛关注."
    result = analyze_event(event_description)
    print("\n=== 分析报告 ===\n")
    print(result["analysis"])
    print("\n=== 相关新闻和参考资料 ===\n")
    for i, search_result in enumerate(result["search_results"], 1):
        print(f"{i}. {search_result.get('title', 'No Title')}")
        print(f"   链接: {search_result.get('link', 'No Link')}")
        print(f"   摘要: {search_result.get('snippet', 'No Snippet')}")
        print()
