# Design Document

## Overview

The Application Integration and Main Entry Point feature provides the foundational infrastructure to bootstrap and run the Meeting Room Reservation System. The design follows Domain-Driven Design principles with clear separation between domain, application, and infrastructure layers. The system uses dependency injection to manage service lifecycles and provides flexible configuration management for different deployment environments.

## Architecture

The application integration follows a layered architecture with dependency injection as the central coordination mechanism:

```
┌─────────────────────────────────────────┐
│              Main Entry Point           │
│  (main.py, CLI argument parsing)        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Application Bootstrap           │
│  (Configuration, DI Container Setup)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│        Dependency Injection             │
│         Container                       │
└─────┬─────────┬─────────┬───────────────┘
      │         │         │
┌─────▼───┐ ┌───▼────┐ ┌──▼──────────────┐
│ Domain  │ │  App   │ │ Infrastructure  │
│ Layer   │ │ Layer  │ │     Layer       │
└─────────┘ └────────┘ └─────────────────┘
```

## Components and Interfaces

### 1. Dependency Injection Container

**Location:** `src/infrastructure/container.py`

The container manages service registration, resolution, and lifecycle management:

```python
class ServiceContainer:
    def register_singleton(self, interface: Type, implementation: Type)
    def register_transient(self, interface: Type, implementation: Type)
    def register_scoped(self, interface: Type, implementation: Type)
    def resolve(self, service_type: Type) -> Any
    def configure_for_environment(self, env: Environment)
```

**Service Lifetimes:**
- **Singleton**: Single instance shared across the application (repositories, configuration)
- **Transient**: New instance created for each request (commands, DTOs)
- **Scoped**: Single instance per operation scope (application services)

### 2. Application Configuration

**Location:** `src/infrastructure/config/`

Configuration management with environment-specific settings:

```python
@dataclass
class ApplicationConfig:
    environment: str
    log_level: str
    log_format: str
    repository_type: str
    
class ConfigurationManager:
    def load_config(self, env: str = None) -> ApplicationConfig
    def validate_config(self, config: ApplicationConfig) -> None
```

**Configuration Sources (in precedence order):**
1. Command-line arguments
2. Environment variables
3. Configuration files (`config/{env}.json`)
4. Default values

### 3. Main Application Entry Point

**Location:** `main.py`

The main entry point coordinates application startup:

```python
class Application:
    def __init__(self, container: ServiceContainer, config: ApplicationConfig)
    def run(self, args: List[str]) -> int
    def shutdown(self) -> None
```

**Startup Sequence:**
1. Parse command-line arguments
2. Load and validate configuration
3. Configure logging
4. Initialize dependency container
5. Register services and repositories
6. Start CLI application
7. Handle graceful shutdown

### 4. Service Registration

Services are registered in the container following DDD layer boundaries:

**Domain Layer Services:**
- No external dependencies
- Pure business logic

**Application Layer Services:**
- `BookingService`, `CancellationService`, `QueryService`
- Depend on domain repositories (abstractions)

**Infrastructure Layer Services:**
- `InMemoryMeetingRoomRepository`
- CLI commands and handlers
- Configuration and logging

## Data Models

### Configuration Model

```python
@dataclass
class ApplicationConfig:
    environment: str = "development"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    repository_type: str = "in_memory"
    
@dataclass  
class LoggingConfig:
    level: str
    format: str
    handlers: List[str]
```

### Service Registration Model

```python
@dataclass
class ServiceRegistration:
    interface: Type
    implementation: Type
    lifetime: ServiceLifetime
    
class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient" 
    SCOPED = "scoped"
```

## Error Handling

### Configuration Errors

- **Invalid configuration values**: Raise `ConfigurationError` with specific field validation messages
- **Missing required settings**: Provide clear error messages indicating missing configuration
- **Environment-specific issues**: Log warnings for development, fail fast in production

### Dependency Injection Errors

- **Circular dependencies**: Detect and report circular dependency chains
- **Missing registrations**: Provide clear error messages when services cannot be resolved
- **Lifetime mismatches**: Validate service lifetime compatibility

### Application Startup Errors

- **Service initialization failures**: Log detailed error information and exit gracefully
- **CLI argument parsing errors**: Display help information and usage examples
- **Resource availability**: Check for required resources and dependencies

## Testing Strategy

### Unit Tests

**Container Tests:**
- Service registration and resolution
- Lifetime management (singleton, transient, scoped)
- Error handling for missing services and circular dependencies

**Configuration Tests:**
- Configuration loading from multiple sources
- Environment-specific configuration validation
- Default value application and override precedence

**Application Bootstrap Tests:**
- Startup sequence validation
- Error handling during initialization
- Graceful shutdown procedures

### Integration Tests

**End-to-End Application Tests:**
- Full application startup with real dependencies
- CLI command execution through main entry point
- Configuration loading in different environments

**Service Wiring Tests:**
- Verify all services can be resolved from container
- Test service interactions through dependency injection
- Validate layer boundary enforcement

### Test Configuration

**Test Environment Setup:**
- Isolated test configuration
- Mock external dependencies
- Test-specific service registrations

**Property-Based Testing:**
- Configuration validation with various input combinations
- Service resolution with different registration scenarios
- Error handling with edge cases

## Implementation Notes

### Environment Support

The system supports three environments:
- **Development**: Verbose logging, relaxed validation
- **Test**: Minimal logging, strict validation, isolated state
- **Production**: Structured logging, fail-fast validation, optimized performance

### Logging Configuration

Each environment has specific logging requirements:
- **Development**: Console output with detailed formatting
- **Test**: Minimal output to avoid test noise
- **Production**: Structured JSON logging for monitoring systems

### Service Registration Order

Services must be registered in dependency order:
1. Configuration and logging
2. Domain repositories (abstractions)
3. Infrastructure repositories (implementations)
4. Application services
5. CLI commands and handlers

### Graceful Shutdown

The application handles shutdown signals:
- Save any pending state
- Close resource connections
- Log shutdown completion
- Return appropriate exit codes