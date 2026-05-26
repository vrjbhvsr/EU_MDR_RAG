from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

class IngestionConfig(BaseModel):
    """Configuration for the data ingestion process."""
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    cache_dir: Path = Path("data/cache")


class Settings(BaseSettings):
    """Application settings for the data ingestion process."""
    ingestion: IngestionConfig = IngestionConfig()

    class Config:
        """Pydantic configuration for the Settings class."""
        env_file = ".env"
        env_nested_delimiter = "__"


def get_settings() -> Settings:
    """Get the application settings.
    This function initializes and returns an instance of the Settings class, which contains the configuration for the data ingestion process. The settings are loaded from environment variables or a .env file if specified.
    Returns:
        Settings: An instance of the Settings class containing the application configuration."""
    return Settings()