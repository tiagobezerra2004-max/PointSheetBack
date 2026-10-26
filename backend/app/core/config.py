from functools import lru_cache

from cryptography.fernet import Fernet
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "pointsheet"
    db_user: str = "pointsheet"
    db_password: SecretStr
    data_encryption_key: SecretStr
    cpf_hash_key: SecretStr
    cors_origins: str = "http://localhost:3000"
    docs_enabled: bool = True

    @field_validator("data_encryption_key")
    @classmethod
    def validate_encryption_key(cls, value: SecretStr) -> SecretStr:
        try:
            Fernet(value.get_secret_value().encode("ascii"))
        except (ValueError, TypeError, UnicodeEncodeError) as error:
            raise ValueError("DATA_ENCRYPTION_KEY deve ser uma chave Fernet válida.") from error
        return value

    @field_validator("cpf_hash_key")
    @classmethod
    def validate_cpf_hash_key(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode("utf-8")) < 32:
            raise ValueError("CPF_HASH_KEY deve conter pelo menos 32 bytes.")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
