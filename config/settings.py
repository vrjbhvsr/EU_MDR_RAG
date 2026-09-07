from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

#########################################################################################
class IngestionConfig(BaseModel):
    """Configuration for the data ingestion process."""
    raw_data_dir: Path = Path("data/raw")
    processed_data_dir: Path = Path("data/processed")
    cache_dir: Path = Path("data/cache")

#------------------------------------------------------------------------------------------
class EmbeddingConfig(BaseModel):
    model_name: str = 'BAAI/bge-base-en-v1.5'

#------------------------------------------------------------------------------------------

class ChunkingConfig(BaseModel):
    """Configuration for Chunking Process."""
    max_tokens: int = 512
    patterns: dict = {
    "part"        : r'\nPART [A-Z] \n(.+)',
    "simple"      : r'\n(\d+)\.\s*\n(.+)',
    "decimal"     : r'(?:^|\n)(\d+\.\d+\.)(?!\d)\s+(.+)',   
    "triple"      : r'(?:^|\n)(\d+\.\d+\.\d+\.)\s+(.+)',
    "paren_letter": r'(?:^|\n)\(([a-z])\)\s+(.+)',          
    "paren_num"   : r'(?:^|\n)\((\d+)\)\s+(.+)',  
    "bullet"      : r'(?:^|\n)(—)\s+(.+)',          
    }

    marker_patterns:dict = {"pattern_annex" : "^(ANNEX [IVX]+) \n(.+)", 
                       "pattern_chapter" : "^(CHAPTER [IVX]+) \n(.+)", 
                       "pattern_section" : "^(SECTION [0-9]+) \n(.+)", 
                       "pattern_article" :"^(Article [0-9]+) \n(?!Article)(?!— )(.+)"}


##############################################################################################

class Settings(BaseSettings):
    """Application settings for the data ingestion process."""
    ingestion: IngestionConfig = IngestionConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    chunking: ChunkingConfig = ChunkingConfig()

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