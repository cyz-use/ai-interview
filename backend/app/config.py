"""应用配置 —— 使用 Pydantic Settings 管理所有环境变量。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，自动从 .env 文件读取。"""

    # ========== LLM ==========
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"

    # ========== Embedding ==========
    embedding_api_key: str = ""
    embedding_base_url: str = "https://api.deepseek.com/v1"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # ========== 数据库（开发默认 SQLite，生产设 PostgreSQL）==========
    database_url: str = "sqlite:///./interview.db"

    # ========== Redis ==========
    redis_url: str = "redis://localhost:6379/0"

    # ========== MinIO ==========
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "interview-files"
    minio_secure: bool = False

    # ========== JWT 认证 ==========
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 小时

    # ========== RAG ==========
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 64
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.7

    # ========== 限流 ==========
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    # ========== 语音 ==========
    dashscope_api_key: str = ""
    asr_provider: str = "dashscope"  # dashscope | openai
    tts_provider: str = "dashscope"  # dashscope | edge_tts

    # ========== 面试配置 ==========
    max_main_questions: int = 5
    max_followups_per_question: int = 3
    pass_score_threshold: float = 70.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# 全局单例
settings = Settings()
