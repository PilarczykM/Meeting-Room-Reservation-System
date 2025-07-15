"""Service registration configuration for dependency injection container."""

from src.application.services.booking_service import BookingService
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository

from .config.models import ApplicationConfig, Environment, RepositoryType
from .container import ServiceContainer
from .repositories.in_memory_repository import InMemoryMeetingRoomRepository


class ServiceConfigurator:
    """Configures service registrations for the dependency injection container."""

    def __init__(self, container: ServiceContainer, config: ApplicationConfig):
        """Initialize the service configurator.

        Args:
            container: The dependency injection container
            config: Application configuration

        """
        self.container = container
        self.config = config

    def configure_all(self) -> None:
        """Configure all services in the correct order."""
        self.configure_repositories()
        self.configure_application_services()
        self.configure_infrastructure_services()
        self._apply_environment_specific_configuration()

    def configure_repositories(self) -> None:
        """Configure domain repositories with their implementations."""
        repository_impl = self._get_repository_implementation(self.config.repository_type)

        # Register repository as singleton (shared across application)
        self.container.register_singleton(MeetingRoomRepository, repository_impl)

    def configure_application_services(self) -> None:
        """Configure application layer services."""
        # Application services are scoped (one instance per operation scope)
        self.container.register_scoped(BookingService, BookingService)
        self.container.register_scoped(CancellationService, CancellationService)
        self.container.register_scoped(QueryService, QueryService)

    def configure_infrastructure_services(self) -> None:
        """Configure infrastructure layer services."""
        # Infrastructure services are typically singletons
        repository_impl = self._get_repository_implementation(self.config.repository_type)

        # Ensure repository implementation is registered
        if not self._is_service_registered(MeetingRoomRepository):
            self.container.register_singleton(MeetingRoomRepository, repository_impl)

    def _get_repository_implementation(self, repository_type: str) -> type:
        """Get the repository implementation class for the given type.

        Args:
            repository_type: The repository type from configuration

        Returns:
            The repository implementation class

        Raises:
            ValueError: If repository type is not supported

        """
        if repository_type == RepositoryType.IN_MEMORY:
            return InMemoryMeetingRoomRepository
        else:
            raise ValueError(f"Unsupported repository type: {repository_type}")

    def _apply_environment_specific_configuration(self) -> None:
        """Apply environment-specific service configurations."""
        if self.config.environment == Environment.DEVELOPMENT:
            self._configure_for_development()
        elif self.config.environment == Environment.TEST:
            self._configure_for_test()
        elif self.config.environment == Environment.PRODUCTION:
            self._configure_for_production()

    def _configure_for_development(self) -> None:
        """Configure services for development environment."""
        # Development-specific configuration
        # Could add debug logging, relaxed validation, etc.
        pass

    def _configure_for_test(self) -> None:
        """Configure services for test environment."""
        # Test-specific configuration
        # Could add test doubles, mocks, etc.
        pass

    def _configure_for_production(self) -> None:
        """Configure services for production environment."""
        # Production-specific configuration
        # Could add performance optimizations, monitoring, etc.
        pass

    def _is_service_registered(self, service_type: type) -> bool:
        """Check if a service type is already registered.

        Args:
            service_type: The service type to check

        Returns:
            True if service is registered, False otherwise

        """
        try:
            self.container.resolve(service_type)
        except Exception:
            return False
        else:
            return True
