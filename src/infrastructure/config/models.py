"""Configuration models with validation."""

from enum import Enum

from pydantic import BaseModel, Field, validator


class Environment(str, Enum):
    """Supported application environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RepositoryType(str, Enum):
    """Supported repository implementations."""

    IN_MEMORY = "in_memory"


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: list[str] = Field(default_factory=lambda: ["console"])

    @validator("handlers")
    def validate_handlers(cls, v):
        """Validate that at least one handler is specified."""
        if not v:
            raise ValueError("At least one logging handler must be specified")
        return v


class ApplicationConfig(BaseModel):
    """Main application configuration with validation."""

    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    repository_type: RepositoryType = RepositoryType.IN_MEMORY
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @validator("logging", pre=True, always=True)
    def set_logging_config(cls, v, values):
        """Ensure logging config is consistent with top-level settings."""
        if isinstance(v, dict):
            v = LoggingConfig(**v)
        elif v is None:
            v = LoggingConfig()

        # Sync top-level log settings with logging config
        if "log_level" in values:
            v.level = values["log_level"]
        if "log_format" in values:
            v.format = values["log_format"]

        return v

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
