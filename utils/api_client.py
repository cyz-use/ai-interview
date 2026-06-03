"""统一 LLM 调用封装 —— 支持 DeepSeek API（OpenAI 兼容接口）。"""

import json
import os
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """延迟创建客户端，避免在导入时就报错。"""
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def llm_call(
    messages: list[dict],
    temperature: float = 0.7,
    response_format: Optional[str] = None,
    max_retries: int = 2,
) -> str:
    """
    调用 DeepSeek Chat API 并返回模型回复文本。

    参数:
        messages: OpenAI 格式的消息列表
        temperature: 采样温度
        response_format: 设为 "json_object" 时强制 JSON 输出
        max_retries: 最大重试次数

    返回:
        模型回复的纯文本内容
    """
    kwargs = dict(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
    )
    if response_format == "json_object":
        kwargs["response_format"] = {"type": "json_object"}

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            client = _get_client()
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(1 * (attempt + 1))

    raise RuntimeError(f"LLM 调用失败（已重试 {max_retries} 次）: {last_error}")
