from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    PROJECT_NAME: str = "Nangarhar University Digital Library"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://postgres:password@localhost:5432/nudl"
    SECRET_KEY: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://127.0.0.1:5500,http://localhost:5500"
    FILE_STORAGE_PATH: str = "private_uploads"
    MAX_FILE_SIZE_MB: int = 30

    @property
    def cors_list(self):
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
