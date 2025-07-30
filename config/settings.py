from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class DatabaseConfig(BaseModel):
    '''Database configuration model with validation.'''

    host: str = Field(..., min_length=1, description='Database host')
    port: int = Field(default=5432,ge=1,le=65535, description='Database port')
    database: str = Field(..., min_length=1, description='Database name')
    user: str = Field(..., min_length=1, description='Database user')
    password: str = Field(..., min_length=1, description='Database password')
    sslmode: str = Field(default='prefer', description='SSL mode')

    @validator('sslmode')
    def validate_sslmode(cls, v):
        valid_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if v not in valid_modes:
            raise ValueError(f"Invalid SSL mode. Must be one of: {valid_modes}")
        return v
    
class Settings(BaseSettings):
    """Application settings loaded from environment varialbes"""

    db_host: str = Field(default = "localhost", env="DB_HOST")
    db_port: int = Field(default = 5432, env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE")

    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        env_file_encoding =  "utf-8"
        case_sensitive = False

    @property
    def database_config(self)-> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            sslmode=self.db_ssl_mode
       )

settings = Settings()