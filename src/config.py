"""Configuration management for the LLM Analysis Quiz application."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # User credentials
    email: str = Field(..., description="User email address")
    secret: str = Field(..., description="Secret string for request verification")
    
    # API configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    api_endpoint_url: str = Field(..., description="Deployed API endpoint URL")
    github_repo_url: str = Field(..., description="GitHub repository URL")
    
    # Application settings
    timeout_seconds: int = Field(default=180, description="Quiz timeout in seconds (3 minutes)")
    max_payload_size: int = Field(default=1048576, description="Maximum payload size in bytes (1MB)")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
