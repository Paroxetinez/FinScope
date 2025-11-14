import tweepy
import os
import logging
import time
from typing import Dict, Optional
from requests.exceptions import ConnectionError, Timeout
from urllib3.exceptions import ProtocolError
from dotenv import load_dotenv

# 重新加载环境变量
load_dotenv(override=True)

# 配置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TwitterPublisher:
    def __init__(self):
        # 记录初始化参数(注意不要记录实际的密钥值)
        logger.debug("Initializing TwitterPublisher with API credentials")

        # 直接从 .env 读取密钥
        self.api_key = ''
        self.api_secret = ''
        self.access_token = ''
        self.access_token_secret = ''

        try:
            # Twitter API v2 认证信息
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            logger.info("Successfully initialized Twitter client")

            # 验证凭据
            try:
                me = self.client.get_me()
                logger.info(
                    f"Successfully authenticated as user ID: {me.data.id}")
            except Exception as e:
                logger.error(f"Failed to verify credentials: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {str(e)}")
            raise

    def format_single_tweet(self, analysis_data: Dict) -> str:
        """将事件分析结果格式化为单条推文"""
        try:
            logger.debug("Formatting tweet content")

            # 获取分析报告的第一段作为概述
            analysis = analysis_data.get('analysis', '')
            if not analysis:
                logger.warning("No analysis data provided")
                return "无法获取分析结果"

            paragraphs = analysis.split('\n\n')
            event_summary = paragraphs[0].replace('事件分析报告:\n', '').strip()
            logger.debug(f"Event summary length: {len(event_summary)}")

            # 获取第一个搜索结果的链接
            link = ""
            if analysis_data.get('search_results') and len(analysis_data['search_results']) > 0:
                link = analysis_data['search_results'][0].get('link', '')
                logger.debug(f"Found reference link: {link}")

            # 添加时间戳,确保内容唯一
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")

            # 组装推文内容
            tweet = f"📢 最新事件分析 ({current_time})\n\n{event_summary}"
            if link:
                tweet += f"\n\n🔗 相关链接:{link}"
            tweet += "\n\n#投资分析 #市场动态 #财经资讯"

            # 确保不超过推特字数限制
            if len(tweet) > 280:
                logger.warning(f"Tweet content too long ({len(tweet)} chars), truncating...")
                tweet = tweet[:277] + "..."

            logger.info(f"Successfully formatted tweet (length: {len(tweet)})")
            return tweet

        except Exception as e:
            logger.error(f"Error formatting tweet: {str(e)}")
            raise

    def publish_single_tweet(self, analysis_data: Dict) -> Optional[str]:
        """发布单条推文,带有重试机制"""
        max_retries = 3
        retry_delay = 5  # 重试间隔秒数

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempt {attempt + 1} of {max_retries} to publish tweet")

                # 格式化推文内容
                tweet = self.format_single_tweet(analysis_data)
                logger.debug(f"Formatted tweet content: {tweet[:50]}...")

                # 发布推文
                logger.debug("Attempting to publish tweet")
                response = self.client.create_tweet(text=tweet)
                logger.info(f"Successfully published tweet with ID: {response.data['id']}")

                # 返回推文内容
                return tweet

            except (ConnectionError, ProtocolError, Timeout) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    logger.info(
                        f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")
                    raise

            except tweepy.errors.Unauthorized as e:
                logger.error(f"Twitter API authentication failed: {str(e)}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error publishing tweet: {str(e)}")
                raise
