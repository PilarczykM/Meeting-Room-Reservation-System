"""Service registration configuration for dependency injection container."""

from src.application.services.booking_service import BookingService
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.config.models import ApplicationConfig, Environment, RepositoryType, StorageType
from src.infrastructure.container import ServiceContainer
from src.infrastructure.exceptions import ServiceConfigurationError
from src.infrastructure.repositories.in_memory_repository import InMemoryMeetingRoomRepository
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository


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
        repository_factory = self._get_repository_factory_from_storage()

        # Register repository factory as singleton (shared across application)
        self.container.register_singleton(MeetingRoomRepository, repository_factory)

    def configure_application_services(self) -> None:
        """Configure application layer services."""
        # Application services are scoped (one instance per operation scope)
        self.container.register_scoped(BookingService, BookingService)
        self.container.register_scoped(CancellationService, CancellationService)
        self.container.register_scoped(QueryService, QueryService)

    def configure_infrastructure_services(self) -> None:
        """Configure infrastructure layer services."""
        # Infrastructure services are typically singletons
        repository_factory = self._get_repository_factory_from_storage()

        # Ensure repository implementation is registered
        if not self._is_service_registered(MeetingRoomRepository):
            self.container.register_singleton(MeetingRoomRepository, repository_factory)

    def _get_repository_implementation_from_storage(self):
        """Get the repository implementation based on storage configuration.

        Returns:
            The repository implementation instance

        Raises:
            ServiceConfigurationError: If storage type is not supported

        """
        storage_type = self.config.storage.type
        storage_path = self.config.storage.path

        try:
            if storage_type == StorageType.JSON:
                return JsonMeetingRoomRepository(storage_path)
            elif storage_type == StorageType.IN_MEMORY:
                return InMemoryMeetingRoomRepository()
            else:
                raise ServiceConfigurationError(  # noqa: TRY301
                    f"Unsupported storage type: {storage_type}",
                    details={"storage_type": storage_type, "storage_path": storage_path},
                )
        except Exception as e:
            if isinstance(e, ServiceConfigurationError):
                raise
            raise ServiceConfigurationError(
                f"Failed to create repository implementation for storage type: {storage_type}",
                details={"storage_type": storage_type, "storage_path": storage_path},
                cause=e,
            ) from e

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
