import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PharmaSentry Backend"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/pharmapp")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AWS / AgentCore Settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DEPLOYED_RUNTIME_URL: str = (
        "https://bedrock-agentcore.ap-south-1.amazonaws.com/runtimes/"
        "arn%3Aaws%3Abedrock-agentcore%3Aap-south-1%3A025066239748%3Aruntime%2Fpharmasentry_PharmaSentryAgent-ApjJvyGvF4/invocations"
    )

    class Config:
        case_sensitive = True

settings = Settings()
