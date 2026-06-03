"""
语音处理服务 —— ASR 语音识别 + TTS 语音合成。

支持提供商：
- dashscope: 阿里云 DashScope（Paraformer ASR + CosyVoice TTS）
- openai: OpenAI Whisper ASR + TTS
- edge_tts: 微软 Edge TTS（免费，仅合成）

开发模式下，ASR 会尝试 DashScope API；TTS 默认用 edge_tts（免费）。
"""

import io
from typing import Optional

from app.config import settings


class VoiceService:
    """语音处理服务 —— 语音识别 + 语音合成。"""

    async def speech_to_text(
        self, audio_data: bytes, audio_format: str = "wav"
    ) -> str:
        """
        语音识别（ASR）。

        参数:
            audio_data: 音频字节数据
            audio_format: 音频格式（wav, mp3, etc.）

        返回:
            识别出的文本
        """
        provider = settings.asr_provider

        if provider == "dashscope":
            return await self._asr_dashscope(audio_data, audio_format)
        elif provider == "openai":
            return await self._asr_openai(audio_data, audio_format)
        else:
            return f"[ASR 未配置（provider={provider}），请设置 DASHSCOPE_API_KEY]"

    async def text_to_speech(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        speed: float = 1.0,
    ) -> Optional[bytes]:
        """
        语音合成（TTS）。

        参数:
            text: 要合成语音的文本
            voice: 语音角色（edge_tts 格式）
            speed: 语速倍率

        返回:
            合成的音频字节（MP3 格式），失败返回 None
        """
        provider = settings.tts_provider

        if provider == "dashscope":
            return await self._tts_dashscope(text)
        elif provider == "edge_tts":
            return await self._tts_edge(text, voice, speed)
        else:
            return None

    # ======================== DashScope ASR ========================

    async def _asr_dashscope(
        self, audio_data: bytes, audio_format: str = "wav"
    ) -> str:
        """使用阿里云 DashScope Paraformer 进行语音识别。"""
        api_key = settings.dashscope_api_key
        if not api_key:
            return "[DashScope API Key 未配置]"

        try:
            import aiohttp

            # DashScope Paraformer 实时转写 API
            url = "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            # 实际调用需要先用文件上传接口获得 file_url，
            # 这里保留结构，生产环境对接 DashScope 完整流程。
            return "[DashScope ASR 已配置，等待音频上传流程对接]"
        except ImportError:
            return "[需要安装 aiohttp: pip install aiohttp]"
        except Exception as e:
            return f"[ASR 失败: {e}]"

    # ======================== OpenAI ASR ========================

    async def _asr_openai(
        self, audio_data: bytes, audio_format: str = "wav"
    ) -> str:
        """使用 OpenAI Whisper API 进行语音识别。"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            return transcript.text
        except Exception as e:
            return f"[OpenAI ASR 失败: {e}]"

    # ======================== DashScope TTS ========================

    async def _tts_dashscope(self, text: str) -> Optional[bytes]:
        """使用阿里云 DashScope CosyVoice 进行语音合成。"""
        api_key = settings.dashscope_api_key
        if not api_key:
            return None

        try:
            import aiohttp

            url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/speech"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "cosyvoice-v1",
                "input": {"text": text},
                "parameters": {"voice": "longxiaochun", "format": "mp3"},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        return None
        except ImportError:
            return None
        except Exception:
            return None

    # ======================== Edge TTS（免费）========================

    async def _tts_edge(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        speed: float = 1.0,
    ) -> Optional[bytes]:
        """使用微软 Edge TTS（免费）进行语音合成。"""
        try:
            import edge_tts

            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=f"{'+' if speed > 1 else ''}{int((speed - 1) * 100)}%",
            )

            audio_chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])

            if audio_chunks:
                return b"".join(audio_chunks)
            return None
        except ImportError:
            return None
        except Exception:
            return None


# 全局单例
voice_service = VoiceService()
