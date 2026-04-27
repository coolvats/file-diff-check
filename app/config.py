"""
Configuration settings for the application
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "File Duplicate Checker API"
    API_VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://0.0.0.0:8000",
    ]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 104857600  # 100 MB
    ALLOWED_EXTENSIONS: List[str] = ["*"]
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # LangSmith Configuration
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_ENDPOINT: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "file-duplicate-checker")
    

    
    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
    GITHUB_OWNER: str = os.getenv("GITHUB_OWNER", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()