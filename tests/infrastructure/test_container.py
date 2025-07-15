"""Tests for the dependency injection container."""

from abc import ABC, abstractmethod
from typing import Protocol

import pytest

from src.infrastructure.container import DependencyInjectionError, ServiceContainer, ServiceLifetime


# Test interfaces and implementations
class ITestService(Protocol):
    """Test service interface."""

    def get_value(self) -> str:
        """Get a test value."""
        ...


class ITestRepository(ABC):
    """Test repository interface."""

    @abstractmethod
    def save(self, data: str) -> None:
        """Save data."""
        pass


class ConcreteTestService:
    """Test service implementation."""

    def __init__(self, repository: ITestRepository):
        self.repository = repository

    def get_value(self) -> str:
        return "test_value"


class ConcreteTestRepository:
    """Test repository implementation."""

    def __init__(self):
        pass

    def save(self, data: str) -> None:
        pass


class SingletonService:
    """Service that should be singleton."""

    def __init__(self):
        self.instance_id = id(self)


class TransientService:
    """Service that should be transient."""

    def __init__(self):
        self.instance_id = id(self)


class CircularServiceA:
    """Service A for circular dependency test."""

    def __init__(self, service_b: "CircularServiceB"):
        self.service_b = service_b


class CircularServiceB:
    """Service B for circular dependency test."""

    def __init__(self, service_a: CircularServiceA):
        self.service_a = service_a


class TestServiceContainer:
    """Test cases for ServiceContainer."""

    def test_container_initialization(self):
        """Test that container can be initialized."""
        container = ServiceContainer()
        assert container is not None

    def test_register_singleton_service(self):
        """Test registering a singleton service."""
        container = ServiceContainer()
        container.register_singleton(ITestRepository, ConcreteTestRepository)

        # Should not raise any exception
        assert True

    def test_register_transient_service(self):
        """Test registering a transient service."""
        container = ServiceContainer()
        container.register_transient(ITestService, ConcreteTestService)

        # Should not raise any exception
        assert True

    def test_register_scoped_service(self):
        """Test registering a scoped service."""
        container = ServiceContainer()
        container.register_scoped(ITestService, ConcreteTestService)

        # Should not raise any exception
        assert True

    def test_resolve_singleton_service(self):
        """Test resolving a singleton service returns same instance."""
        container = ServiceContainer()
        container.register_singleton(SingletonService, SingletonService)

        instance1 = container.resolve(SingletonService)
        instance2 = container.resolve(SingletonService)

        assert instance1 is instance2
        assert instance1.instance_id == instance2.instance_id

    def test_resolve_transient_service(self):
        """Test resolving a transient service returns new instances."""
        container = ServiceContainer()
        container.register_transient(TransientService, TransientService)

        instance1 = container.resolve(TransientService)
        instance2 = container.resolve(TransientService)

        assert instance1 is not instance2
        assert instance1.instance_id != instance2.instance_id

    def test_resolve_service_with_dependencies(self):
        """Test resolving a service that has dependencies."""
        container = ServiceContainer()
        container.register_singleton(ITestRepository, ConcreteTestRepository)
        container.register_transient(ITestService, ConcreteTestService)

        service = container.resolve(ITestService)

        assert isinstance(service, ConcreteTestService)
        assert isinstance(service.repository, ConcreteTestRepository)
        assert service.get_value() == "test_value"

    def test_resolve_unregistered_service_raises_error(self):
        """Test that resolving unregistered service raises error."""
        container = ServiceContainer()

        with pytest.raises(DependencyInjectionError) as exc_info:
            container.resolve(ITestService)

        assert "not registered" in str(exc_info.value).lower()

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected and raise error."""
        container = ServiceContainer()
        container.register_transient(CircularServiceA, CircularServiceA)
        container.register_transient(CircularServiceB, CircularServiceB)

        with pytest.raises(DependencyInjectionError) as exc_info:
            container.resolve(CircularServiceA)

        assert "circular dependency" in str(exc_info.value).lower()

    def test_scoped_service_lifetime(self):
        """Test that scoped services return same instance within scope."""
        container = ServiceContainer()
        container.register_scoped(TransientService, TransientService)

        with container.create_scope() as scope:
            instance1 = scope.resolve(TransientService)
            instance2 = scope.resolve(TransientService)

            assert instance1 is instance2
            assert instance1.instance_id == instance2.instance_id

        # New scope should create new instance
        with container.create_scope() as scope:
            instance3 = scope.resolve(TransientService)
            assert instance3.instance_id != instance1.instance_id

    def test_configure_for_environment(self):
        """Test environment-specific configuration."""
        container = ServiceContainer()

        # Should not raise exception
        container.configure_for_environment("development")
        container.configure_for_environment("test")
        container.configure_for_environment("production")

    def test_service_lifetime_enum(self):
        """Test ServiceLifetime enum values."""
        assert ServiceLifetime.SINGLETON.value == "singleton"
        assert ServiceLifetime.TRANSIENT.value == "transient"
        assert ServiceLifetime.SCOPED.value == "scoped"

    def test_dependency_injection_error_with_details(self):
        """Test DependencyInjectionError with details."""
        error = DependencyInjectionError("Test error", {"service": "TestService"})

        assert str(error) == "Test error"
        assert error.details == {"service": "TestService"}

    def test_register_duplicate_service_overwrites(self):
        """Test that registering same service twice overwrites the first registration."""
        container = ServiceContainer()

        container.register_singleton(SingletonService, SingletonService)
        container.register_transient(SingletonService, SingletonService)  # Should overwrite

        instance1 = container.resolve(SingletonService)
        instance2 = container.resolve(SingletonService)

        # Should be transient now (different instances)
        assert instance1 is not instance2
