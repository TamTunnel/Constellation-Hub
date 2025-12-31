"""
Configuration management for Constellation Hub services.
All configuration is loaded from environment variables.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://constellation:constellation@localhost:5432/constellation_hub"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Service URLs
    core_orbits_url: str = "http://localhost:8001"
    routing_url: str = "http://localhost:8002"
    ground_scheduler_url: str = "http://localhost:8003"
    ai_agents_url: str = "http://localhost:8004"
    
    # AI/LLM
    llm_provider: str = "mock"  # mock, openai, anthropic, local
    llm_api_key: str = ""
    llm_model: str = "gpt-4"
    
    # Logging
    log_level: str = "INFO"
    
    # Development
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
