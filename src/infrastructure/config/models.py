"""Configuration models with validation."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class StorageType(str, Enum):
    """Supported storage implementations."""

    JSON = "json"
    IN_MEMORY = "in_memory"


class StorageConfig(BaseModel):
    """Storage configuration settings."""

    type: StorageType = StorageType.JSON
    path: str = "data/meeting_rooms"


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: list[str] = Field(default_factory=lambda: ["console"])

    @field_validator("handlers")
    @classmethod
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
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
    )

    @field_validator("storage", mode="before")
    @classmethod
    def set_storage_config(cls, v):
        """Ensure storage config is properly initialized."""
        if isinstance(v, dict):
            v = StorageConfig(**v)
        elif v is None:
            v = StorageConfig()
        return v

    @field_validator("logging", mode="before")
    @classmethod
    def set_logging_config(cls, v):
        """Ensure logging config is consistent with top-level settings."""
        if isinstance(v, dict):
            v = LoggingConfig(**v)
        elif v is None:
            v = LoggingConfig()
        return v

    @model_validator(mode="after")
    def sync_logging_config(self):
        """Sync top-level log settings with logging config."""
        # Update logging config to match top-level settings
        self.logging.level = self.log_level
        self.logging.format = self.log_format
        return self
