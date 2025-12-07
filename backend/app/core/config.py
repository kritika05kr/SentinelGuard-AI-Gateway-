from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SentinelGuard AI Gateway"
    API_V1_PREFIX: str = "/api"
    ENV: str = "development"

    # RAG / policy
    POLICY_VECTOR_STORE_PATH: str = "ml_models/vector_store_faiss"
    POLICY_CHUNKS_PATH: str = "policies/chunked_policies.json"

    # Risk thresholds
    RISK_LOW_THRESHOLD: int = 30
    RISK_HIGH_THRESHOLD: int = 70

    class Config:
        env_file = ".env"


settings = Settings()
