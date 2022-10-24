from pydantic import BaseModel, BaseSettings, Field, SecretStr


class Database(BaseSettings):
    user: str = Field(..., env="POSTGRES_USER")
    password: SecretStr = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field(..., env="POSTGRES_HOST")
    name: str = Field(..., env="POSTGRES_DB")
    pool_size: int = Field(..., env="POSTGRES_POOL_SIZE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings(BaseModel):
    db: Database = Field(default_factory=Database)
    sqlite: bool = False


settings = Settings()
