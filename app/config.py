from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import secrets

class Settings(BaseSettings):
    # App
    app_name: str = "FastAPI Organization"
    debug: bool = False
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "organization_db"
    
    # Security
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "forbid"

@lru_cache()
def get_settings() -> Settings:
    return Settings()