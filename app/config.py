from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = Field("LangOps NER API", env="APP_NAME")
    environment: str = Field("development", env="ENVIRONMENT")
    port: int = Field(3000, env="PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    analyzer_conf_file: Optional[str] = Field(None, env="ANALYZER_CONF_FILE")
    nlp_conf_file: Optional[str] = Field(None, env="NLP_CONF_FILE")
    recognizer_registry_conf_file: Optional[str] = Field(None, env="RECOGNIZER_REGISTRY_CONF_FILE")
    cors_origins: List[str] = Field(["*"], env="CORS_ORIGINS")
    
    @field_validator('environment')
    def validate_environment(cls, v):
        if v.lower() not in {'development', 'production'}:
            return 'development'
        return v.lower()
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        allowed = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        return v.upper() if v.upper() in allowed else 'INFO'

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    
    from pathlib import Path
    base = Path(__file__).parent.parent
    app_base = Path(__file__).parent
    
    
    if settings.analyzer_conf_file:
        config_path = base / settings.analyzer_conf_file
        if not config_path.exists():
            
            app_config_path = app_base / "config" / Path(settings.analyzer_conf_file).name
            if app_config_path.exists():
                settings.analyzer_conf_file = str(app_config_path)
            else:
                settings.analyzer_conf_file = str(config_path)
        else:
            settings.analyzer_conf_file = str(config_path)
    
    if settings.nlp_conf_file:
        config_path = base / settings.nlp_conf_file 
        if not config_path.exists():
            
            app_config_path = app_base / "config" / Path(settings.nlp_conf_file).name
            if app_config_path.exists():
                settings.nlp_conf_file = str(app_config_path)
            else:
                settings.nlp_conf_file = str(config_path)
        else:
            settings.nlp_conf_file = str(config_path)
    
    if settings.recognizer_registry_conf_file:
        config_path = base / settings.recognizer_registry_conf_file
        if not config_path.exists():
            
            app_config_path = app_base / "config" / Path(settings.recognizer_registry_conf_file).name
            if app_config_path.exists():
                settings.recognizer_registry_conf_file = str(app_config_path)
            else:
                settings.recognizer_registry_conf_file = str(config_path)
        else:
            settings.recognizer_registry_conf_file = str(config_path)
    
    return settings

def configure_logging() -> None:
    import logging
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(name)s %(levelname)s - %(message)s",
    )
