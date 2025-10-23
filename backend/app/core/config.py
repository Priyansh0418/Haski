from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./haski.db'
    secret_key: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24  # default: 1 day


settings = Settings()
