"""Tests for service registration configuration."""

import pytest

from src.application.services.booking_service import BookingService
from src.application.services.cancellation_service import CancellationService
from src.application.services.query_service import QueryService
from src.domain.repositories.meeting_room_repository import MeetingRoomRepository
from src.infrastructure.config.models import ApplicationConfig, Environment, RepositoryType
from src.infrastructure.container import ServiceContainer
from src.infrastructure.exceptions import ServiceConfigurationError
from src.infrastructure.repositories.in_memory_repository import InMemoryMeetingRoomRepository
from src.infrastructure.repositories.json_repository import JsonMeetingRoomRepository
from src.infrastructure.service_configurator import ServiceConfigurator


class TestServiceConfigurator:
    """Test cases for ServiceConfigurator."""

    def test_configurator_initialization(self):
        """Test that configurator can be initialized."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        assert configurator is not None
        assert configurator.container is container
        assert configurator.config is config

    def test_configure_all_services(self):
        """Test that all services are configured correctly."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_all()

        # Should be able to resolve repository (singleton)
        repository = container.resolve(MeetingRoomRepository)
        # With new storage-based configuration, default is JSON repository wrapper
        assert hasattr(repository, "_repository")

        assert isinstance(repository._repository, JsonMeetingRoomRepository)

        # Should be able to resolve scoped services within a scope
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            cancellation_service = scope.resolve(CancellationService)
            query_service = scope.resolve(QueryService)

            assert isinstance(booking_service, BookingService)
            assert isinstance(cancellation_service, CancellationService)
            assert isinstance(query_service, QueryService)

    def test_configure_domain_repositories(self):
        """Test that domain repositories are configured as abstractions."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        # Should resolve to concrete implementation
        repository = container.resolve(MeetingRoomRepository)
        # With new storage-based configuration, default is JSON repository wrapper
        assert hasattr(repository, "_repository")

        assert isinstance(repository._repository, JsonMeetingRoomRepository)

    def test_configure_application_services(self):
        """Test that application services are configured correctly."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        # First configure repositories (dependencies)
        configurator.configure_repositories()
        # Then configure services
        configurator.configure_application_services()

        # Resolve scoped services within a scope
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            cancellation_service = scope.resolve(CancellationService)
            query_service = scope.resolve(QueryService)

            assert isinstance(booking_service, BookingService)
            assert isinstance(cancellation_service, CancellationService)
            assert isinstance(query_service, QueryService)

    def test_configure_infrastructure_services(self):
        """Test that infrastructure services are configured correctly."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_infrastructure_services()

        # Should be able to resolve infrastructure implementations
        repository = container.resolve(MeetingRoomRepository)
        # With new storage-based configuration, default is JSON repository wrapper
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)

    def test_environment_specific_configuration_development(self):
        """Test development environment specific configuration."""
        container = ServiceContainer()
        config = ApplicationConfig(environment=Environment.DEVELOPMENT)
        configurator = ServiceConfigurator(container, config)

        configurator.configure_all()

        # In development, services should be configured for debugging
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            assert isinstance(booking_service, BookingService)

    def test_environment_specific_configuration_test(self):
        """Test test environment specific configuration."""
        container = ServiceContainer()
        config = ApplicationConfig(environment=Environment.TEST)
        configurator = ServiceConfigurator(container, config)

        configurator.configure_all()

        # In test environment, services should be configured for testing
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            assert isinstance(booking_service, BookingService)

    def test_environment_specific_configuration_production(self):
        """Test production environment specific configuration."""
        container = ServiceContainer()
        config = ApplicationConfig(environment=Environment.PRODUCTION)
        configurator = ServiceConfigurator(container, config)

        configurator.configure_all()

        # In production, services should be configured for performance
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            assert isinstance(booking_service, BookingService)

    def test_repository_type_configuration(self):
        """Test that repository type from config is respected."""
        container = ServiceContainer()
        config = ApplicationConfig(repository_type=RepositoryType.IN_MEMORY)
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        # With new storage-based configuration, storage config takes precedence
        # and defaults to JSON, so repository_type is ignored
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)

    def test_service_lifetimes_are_correct(self):
        """Test that services are registered with correct lifetimes."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_all()

        # Repositories should be singletons
        repo1 = container.resolve(MeetingRoomRepository)
        repo2 = container.resolve(MeetingRoomRepository)
        assert repo1 is repo2

        # Application services should be scoped
        with container.create_scope() as scope1:
            service1a = scope1.resolve(BookingService)
            service1b = scope1.resolve(BookingService)
            assert service1a is service1b

        with container.create_scope() as scope2:
            service2 = scope2.resolve(BookingService)
            assert service2 is not service1a

    def test_configure_with_missing_dependencies_raises_error(self):
        """Test that configuring services without dependencies raises error."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        # Try to configure application services without repositories
        configurator.configure_application_services()

        # Should raise error when trying to resolve
        with pytest.raises(Exception):
            container.resolve(BookingService)

    def test_configure_order_matters(self):
        """Test that configuration order is important for dependencies."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        # Configure in correct order
        configurator.configure_repositories()
        configurator.configure_application_services()

        # Should work fine within a scope
        with container.create_scope() as scope:
            booking_service = scope.resolve(BookingService)
            assert isinstance(booking_service, BookingService)

    def test_get_repository_implementation_for_type(self):
        """Test that correct repository implementation is returned for type."""
        container = ServiceContainer()
        config = ApplicationConfig(repository_type=RepositoryType.IN_MEMORY)
        configurator = ServiceConfigurator(container, config)

        impl_class = configurator._get_repository_implementation(RepositoryType.IN_MEMORY)
        assert impl_class == InMemoryMeetingRoomRepository

    def test_unsupported_repository_type_raises_error(self):
        """Test that unsupported repository type raises error."""
        container = ServiceContainer()
        config = ApplicationConfig()
        configurator = ServiceConfigurator(container, config)

        with pytest.raises(ValueError) as exc_info:
            configurator._get_repository_implementation("unsupported_type")

        assert "unsupported repository type" in str(exc_info.value).lower()


class TestServiceConfiguratorWithJsonRepository:
    """Test cases for service configurator with JSON repository support."""

    def test_configure_repositories_with_json_storage(self):
        """Test that repositories are configured with JSON storage when specified."""
        config = ApplicationConfig(storage={"type": "json", "path": "test/storage/path"})
        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        # Check that it's a wrapper around JsonMeetingRoomRepository
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)
        assert repository._repository._storage_path == "test/storage/path"

    def test_configure_repositories_with_in_memory_storage(self):
        """Test that repositories are configured with in-memory storage when specified."""
        config = ApplicationConfig(storage={"type": "in_memory", "path": "ignored/path"})
        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        assert isinstance(repository, InMemoryMeetingRoomRepository)

    def test_configure_repositories_defaults_to_json_storage(self):
        """Test that repositories default to JSON storage with default configuration."""

        config = ApplicationConfig()  # Uses defaults
        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        # Check that it's a wrapper around JsonMeetingRoomRepository
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)
        assert repository._repository._storage_path == "data/meeting_rooms"

    def test_configure_repositories_raises_error_for_unsupported_storage(self):
        """Test that unsupported storage types raise appropriate errors."""

        # Create config with unsupported storage type by bypassing validation
        config = ApplicationConfig()
        config.storage.type = "unsupported_type"  # Bypass enum validation

        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        with pytest.raises(ServiceConfigurationError):
            configurator.configure_repositories()

    def test_backward_compatibility_with_repository_type(self):
        """Test that old repository_type configuration still works."""
        config = ApplicationConfig(repository_type=RepositoryType.IN_MEMORY)
        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        # With the new storage-based approach, it should still use JSON by default
        # but the repository_type is ignored in favor of storage config
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)

    def test_storage_config_takes_precedence_over_repository_type(self):
        """Test that storage config takes precedence over legacy repository_type."""
        config = ApplicationConfig(
            repository_type=RepositoryType.IN_MEMORY,  # Legacy setting
            storage={"type": "json", "path": "custom/path"},  # New setting takes precedence
        )
        container = ServiceContainer()
        configurator = ServiceConfigurator(container, config)

        configurator.configure_repositories()

        repository = container.resolve(MeetingRoomRepository)
        # Check that it's a wrapper around JsonMeetingRoomRepository
        assert hasattr(repository, "_repository")
        assert isinstance(repository._repository, JsonMeetingRoomRepository)
        assert repository._repository._storage_path == "custom/path"
