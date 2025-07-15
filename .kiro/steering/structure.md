# Project Structure & Architecture

## Architecture Pattern
Follows **Clean Architecture** with **Domain-Driven Design (DDD)** principles:
- Domain layer contains business logic and rules
- Application layer orchestrates use cases
- Infrastructure layer handles external concerns

## Directory Structure

### Core Application (`src/`)
```
src/
├── domain/           # Business logic and domain models
│   ├── aggregates/   # Domain aggregate roots (MeetingRoom)
│   ├── entities/     # Domain entities (Booking, TimeSlot)
│   ├── repositories/ # Repository interfaces
│   └── exceptions.py # Domain-specific exceptions
├── application/      # Use cases and application services
│   ├── commands/     # Command objects for operations
│   ├── dtos/         # Data transfer objects
│   ├── services/     # Application services (BookingService, etc.)
│   └── exceptions.py # Application-specific exceptions
└── infrastructure/   # External concerns and implementations
    ├── cli/          # Command-line interface
    ├── config/       # Configuration management
    ├── repositories/ # Repository implementations
    ├── container.py  # Dependency injection container
    └── application.py # Application bootstrap
```

### Testing (`tests/`)
- Mirrors `src/` structure exactly
- Each module has corresponding test file
- `conftest.py` contains shared test fixtures
- `test_project_structure.py` validates architectural boundaries

### Configuration (`config/`)
- Environment-specific JSON files
- `development.json`, `production.json`, `test.json`

## Key Architectural Principles

### Dependency Direction
- Domain layer has no dependencies on other layers
- Application layer depends only on domain
- Infrastructure layer depends on both application and domain
- Dependencies point inward (toward domain)

### Naming Conventions
- **Aggregates**: Noun representing business concept (MeetingRoom)
- **Entities**: Domain objects with identity (Booking, TimeSlot)
- **Services**: End with "Service" (BookingService, QueryService)
- **Commands**: End with "Command" (CreateBookingCommand)
- **DTOs**: End with "Request" or "Response" (BookingRequest, BookingResponse)
- **Exceptions**: End with "Error" (BookingNotFoundError)

### File Organization
- One class per file (with matching filename)
- `__init__.py` files for package structure
- Related classes grouped in same directory
- Test files prefixed with `test_`

### Entry Points
- `main.py`: Application entry point with argument parsing
- `src/infrastructure/application.py`: Application bootstrap and lifecycle
- `src/infrastructure/cli/app.py`: CLI command registration and execution

## Dependency Injection
- Custom DI container in `src/infrastructure/container.py`
- Supports singleton, transient, and scoped lifetimes
- Services registered in `src/infrastructure/service_configurator.py`
- Constructor injection with type annotations required