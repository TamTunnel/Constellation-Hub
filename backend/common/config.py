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
    
    # Authentication
    auth_disabled: bool = False  # Set True for local dev without auth
    jwt_secret_key: str = "change-me-in-production-use-a-real-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours
    
    # Demo Mode
    demo_mode: bool = True
    admin_api_key: str = ""  # Optional API key for service-to-service calls
    
    # AI/LLM
    llm_provider: str = "mock"  # mock, openai, anthropic, local
    llm_api_key: str = ""
    llm_model: str = "gpt-4"
    
    # TLE Feeds
    tle_refresh_interval_hours: int = 6
    celestrak_base_url: str = "https://celestrak.org"
    
    # Observability
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    metrics_enabled: bool = True
    
    # Development
    debug: bool = False
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
