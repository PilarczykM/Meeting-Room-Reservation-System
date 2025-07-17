# Design Document

## Overview

The CLI Command Registration feature integrates existing CLI command implementations with the CLI application during application bootstrap. The design leverages the existing dependency injection container to resolve required services and create command handler instances, then registers them with the CLI application. This approach maintains clean separation of concerns while ensuring all commands are properly wired and available for user interaction.

## Architecture

The CLI command registration follows the existing application bootstrap pattern and integrates with the dependency injection system:

```
┌─────────────────────────────────────────┐
│         Application Bootstrap           │
│    (src/infrastructure/application.py)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      CLI Application Creation           │
│         (_create_cli_app)               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Service Resolution & Command         │
│         Handler Creation                │
└─────┬─────────┬─────────┬───────────────┘
      │         │         │
┌─────▼───┐ ┌───▼────┐ ┌──▼──────────────┐
│Booking  │ │Cancel  │ │     List        │
│Command  │ │Command │ │   Command       │
└─────┬───┘ └───┬────┘ └──┬──────────────┘
      │         │         │
┌─────▼─────────▼─────────▼───────────────┐
│           CLI Application               │
│        (register_command)               │
└─────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Enhanced Application Bootstrap

**Location:** `src/infrastructure/application.py`

The `_create_cli_app` method will be enhanced to register CLI commands:

```python
def _create_cli_app(self) -> None:
    """Create the CLI application and register commands."""
    self.cli_app = CLIApp()
    
    # Register CLI commands with dependency injection
    self._register_cli_commands()

def _register_cli_commands(self) -> None:
    """Register all CLI commands with their dependencies."""
    try:
        with self.container.create_scope() as scope:
            # Resolve required services
            booking_service = scope.resolve(BookingService)
            cancellation_service = scope.resolve(CancellationService)
            query_service = scope.resolve(QueryService)
            
            # Create and register command handlers
            self._register_booking_command(booking_service)
            self._register_cancellation_command(cancellation_service, query_service)
            self._register_list_command(query_service)
            
    except Exception as e:
        raise ApplicationError(f"Failed to register CLI commands: {e}") from e
```

### 2. Command Registration Methods

Individual registration methods for each command type:

```python
def _register_booking_command(self, booking_service: BookingService) -> None:
    """Register the booking command."""
    booking_command = BookingCommand(booking_service)
    self.cli_app.register_command("book", booking_command.execute)

def _register_cancellation_command(self, cancellation_service: CancellationService, 
                                 query_service: QueryService) -> None:
    """Register the cancellation command."""
    cancellation_command = CancellationCommand(cancellation_service, query_service)
    self.cli_app.register_command("cancel", cancellation_command.execute)

def _register_list_command(self, query_service: QueryService) -> None:
    """Register the list command."""
    list_command = ListCommand(query_service)
    self.cli_app.register_command("list", list_command.execute)
```

### 3. Command Handler Integration

**Existing Command Classes:** (No changes required)
- `BookingCommand` - Interactive booking with validation
- `CancellationCommand` - Interactive cancellation with confirmation
- `ListCommand` - Formatted listing with sorting options

**Command Interface Contract:**
```python
class CommandHandler:
    def __init__(self, *services):
        """Initialize with required services from DI container."""
        pass
    
    def execute(self, args: List[str]) -> None:
        """Execute the command with provided arguments."""
        pass
```

### 4. Service Dependencies

**Required Services for Commands:**
- `BookingService` - For creating new bookings
- `CancellationService` - For canceling existing bookings  
- `QueryService` - For retrieving booking information

**Service Resolution Pattern:**
```python
# Use scoped resolution to ensure proper service lifecycle
with self.container.create_scope() as scope:
    service = scope.resolve(ServiceType)
```

## Data Models

### Command Registration Model

```python
@dataclass
class CommandRegistration:
    name: str
    handler: Callable[[List[str]], None]
    description: str
    
class CLICommandRegistry:
    def __init__(self, cli_app: CLIApp):
        self.cli_app = cli_app
        self.registrations: List[CommandRegistration] = []
    
    def register(self, name: str, handler: Callable, description: str = None):
        """Register a command with the CLI application."""
        self.cli_app.register_command(name, handler)
        self.registrations.append(CommandRegistration(name, handler, description))
```

### Service Resolution Context

```python
@dataclass
class CommandContext:
    container: ServiceContainer
    scope: ServiceScope
    services: Dict[Type, Any]
    
    def resolve_service(self, service_type: Type) -> Any:
        """Resolve a service within the command context."""
        if service_type not in self.services:
            self.services[service_type] = self.scope.resolve(service_type)
        return self.services[service_type]
```

## Error Handling

### Service Resolution Errors

**Missing Service Registration:**
```python
try:
    service = scope.resolve(ServiceType)
except DependencyInjectionError as e:
    raise ApplicationError(f"Required service {ServiceType.__name__} not registered: {e}")
```

**Service Creation Failures:**
```python
try:
    command = CommandClass(service)
except Exception as e:
    raise ApplicationError(f"Failed to create {CommandClass.__name__}: {e}")
```

### Command Registration Errors

**Duplicate Command Names:**
- Log warning if command name already exists
- Allow override with warning message
- Maintain registration order for help display

**Command Handler Validation:**
```python
def _validate_command_handler(self, handler: Callable) -> None:
    """Validate that handler is callable and has correct signature."""
    if not callable(handler):
        raise ApplicationError(f"Command handler must be callable")
    
    # Check signature has args parameter
    sig = inspect.signature(handler)
    if 'args' not in sig.parameters:
        raise ApplicationError(f"Command handler must accept 'args' parameter")
```

### Runtime Command Errors

**Command Execution Failures:**
- Commands handle their own errors internally
- Application bootstrap only handles registration errors
- CLI app handles unknown command errors

## Testing Strategy

### Unit Tests

**Command Registration Tests:**
```python
def test_register_cli_commands_success():
    """Test successful command registration."""
    # Setup container with required services
    # Call _register_cli_commands()
    # Verify all commands are registered

def test_register_cli_commands_missing_service():
    """Test error handling when required service is missing."""
    # Setup container without required service
    # Expect ApplicationError during registration

def test_command_handler_creation():
    """Test command handler instantiation with services."""
    # Create services
    # Instantiate command handlers
    # Verify handlers are properly initialized
```

**Service Resolution Tests:**
```python
def test_service_resolution_in_scope():
    """Test service resolution within command registration scope."""
    # Create container with scoped services
    # Resolve services within scope
    # Verify correct instances are returned

def test_scope_cleanup_after_registration():
    """Test that service scope is properly cleaned up."""
    # Register commands
    # Verify scope is disposed
    # Verify no resource leaks
```

### Integration Tests

**End-to-End Command Tests:**
```python
def test_full_application_with_commands():
    """Test complete application startup with command registration."""
    # Bootstrap full application
    # Verify all commands are available
    # Execute sample commands
    # Verify proper functionality

def test_command_execution_flow():
    """Test command execution through CLI application."""
    # Register commands
    # Execute commands with various arguments
    # Verify proper service interaction
```

**Error Scenario Tests:**
```python
def test_application_startup_with_registration_failure():
    """Test application behavior when command registration fails."""
    # Simulate registration failure
    # Verify graceful error handling
    # Verify application doesn't start with partial registration
```

### Command-Specific Tests

**Individual Command Tests:**
- Existing command tests remain unchanged
- Commands are tested in isolation with mock services
- Integration tests verify command registration and execution

## Implementation Notes

### Registration Order

Commands should be registered in a consistent order for help display:
1. `book` - Primary user action (creating bookings)
2. `cancel` - Secondary user action (removing bookings)  
3. `list` - Query action (viewing bookings)

### Service Scope Management

- Use scoped service resolution during command registration
- Ensure proper scope cleanup after registration
- Commands receive service instances, not the container itself

### Error Recovery

- If individual command registration fails, log error but continue with other commands
- If critical services are missing, fail application startup completely
- Provide clear error messages for troubleshooting

### Performance Considerations

- Command registration happens once during application startup
- Service resolution is cached within the registration scope
- No performance impact on command execution after registration

### Extensibility

The design supports easy addition of new commands:
1. Create new command class following existing pattern
2. Add registration method in `_register_cli_commands`
3. Register with appropriate command name

### Backward Compatibility

- Existing CLI infrastructure remains unchanged
- Command classes maintain their current interfaces
- Service registration and resolution patterns are preserved