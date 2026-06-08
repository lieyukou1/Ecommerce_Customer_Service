from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = ENV_FILE_DIR / ".env"


class Settings(BaseSettings):
    """
    功能：集中管理项目运行所需的环境配置。
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_model: str
    llm_base_url: str
    llm_api_key: str
    commerce_api_base_url: str
    database_url: str
    app_host: str
    app_port: int


settings = Settings()
