"""Dependency injection container for service management."""

import inspect
from contextlib import contextmanager
from enum import Enum
from threading import Lock
from typing import Any, TypeVar

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Service lifetime enumeration."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class DependencyInjectionError(Exception):
    """Raised when dependency injection fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class ServiceRegistration:
    """Represents a service registration."""

    def __init__(self, interface: type, implementation: type, lifetime: ServiceLifetime):
        self.interface = interface
        self.implementation = implementation
        self.lifetime = lifetime


class ServiceScope:
    """Represents a service scope for scoped services."""

    def __init__(self, container: "ServiceContainer"):
        self._container = container
        self._scoped_instances: dict[type, Any] = {}
        self._lock = Lock()

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service within this scope."""
        registration = self._container._get_registration(service_type)

        if registration.lifetime == ServiceLifetime.SCOPED:
            with self._lock:
                if service_type not in self._scoped_instances:
                    self._scoped_instances[service_type] = self._container._create_instance(registration, self)
                return self._scoped_instances[service_type]
        else:
            return self._container._resolve_with_scope(service_type, self)


class ServiceContainer:
    """Dependency injection container for managing service lifetimes and dependencies."""

    def __init__(self):
        self._registrations: dict[type, ServiceRegistration] = {}
        self._singleton_instances: dict[type, Any] = {}
        self._lock = Lock()

    def register_singleton(self, interface: type, implementation: type) -> None:
        """Register a service with singleton lifetime.

        Args:
            interface: The service interface/type
            implementation: The concrete implementation

        """
        with self._lock:
            self._registrations[interface] = ServiceRegistration(interface, implementation, ServiceLifetime.SINGLETON)

    def register_transient(self, interface: type, implementation: type) -> None:
        """Register a service with transient lifetime.

        Args:
            interface: The service interface/type
            implementation: The concrete implementation

        """
        with self._lock:
            self._registrations[interface] = ServiceRegistration(interface, implementation, ServiceLifetime.TRANSIENT)

    def register_scoped(self, interface: type, implementation: type) -> None:
        """Register a service with scoped lifetime.

        Args:
            interface: The service interface/type
            implementation: The concrete implementation

        """
        with self._lock:
            self._registrations[interface] = ServiceRegistration(interface, implementation, ServiceLifetime.SCOPED)

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a service instance.

        Args:
            service_type: The service type to resolve

        Returns:
            An instance of the requested service

        Raises:
            DependencyInjectionError: If service cannot be resolved

        """
        return self._resolve_with_scope(service_type, None)

    @contextmanager
    def create_scope(self):
        """Create a new service scope for scoped services."""
        scope = ServiceScope(self)
        try:
            yield scope
        finally:
            # Cleanup scope resources if needed
            pass

    def configure_for_environment(self, environment: str) -> None:
        """Configure container for specific environment.

        Args:
            environment: Environment name (development, test, production)

        """
        # Environment-specific configuration can be added here
        # For now, this is a placeholder
        pass

    def _resolve_with_scope(self, service_type: type[T], scope: ServiceScope | None) -> T:
        """Resolve service with optional scope context."""
        registration = self._get_registration(service_type)

        if registration.lifetime == ServiceLifetime.SINGLETON:
            return self._get_or_create_singleton(registration)
        elif registration.lifetime == ServiceLifetime.TRANSIENT:
            return self._create_instance(registration, scope)
        elif registration.lifetime == ServiceLifetime.SCOPED:
            if scope is None:
                raise DependencyInjectionError(f"Scoped service {service_type.__name__} requires a scope context")
            return scope.resolve(service_type)
        else:
            raise DependencyInjectionError(f"Unknown service lifetime: {registration.lifetime}")

    def _get_registration(self, service_type: type) -> ServiceRegistration:
        """Get service registration or raise error if not found."""
        if service_type not in self._registrations:
            raise DependencyInjectionError(
                f"Service {service_type.__name__} is not registered", details={"service_type": service_type.__name__}
            )
        return self._registrations[service_type]

    def _get_or_create_singleton(self, registration: ServiceRegistration) -> Any:
        """Get existing singleton instance or create new one."""
        with self._lock:
            if registration.interface not in self._singleton_instances:
                self._singleton_instances[registration.interface] = self._create_instance(registration, None)
            return self._singleton_instances[registration.interface]

    def _create_instance(self, registration: ServiceRegistration, scope: ServiceScope | None) -> Any:
        """Create a new instance of the service with dependency injection."""
        return self._create_instance_with_dependencies(registration.implementation, scope, set())

    def _create_instance_with_dependencies(
        self, implementation: type, scope: ServiceScope | None, resolution_stack: set[type]
    ) -> Any:
        """Create instance with dependency injection and circular dependency detection."""
        if implementation in resolution_stack:
            cycle = " -> ".join([t.__name__ for t in resolution_stack]) + f" -> {implementation.__name__}"
            raise DependencyInjectionError(f"Circular dependency detected: {cycle}", details={"cycle": cycle})

        resolution_stack.add(implementation)

        try:
            # Get constructor signature
            signature = inspect.signature(implementation.__init__)
            parameters = list(signature.parameters.values())[1:]  # Skip 'self'

            # Resolve dependencies
            dependencies = []
            for param in parameters:
                if param.annotation == inspect.Parameter.empty:
                    raise DependencyInjectionError(
                        f"Parameter {param.name} in {implementation.__name__} has no type annotation"
                    )

                # Handle string annotations (forward references)
                annotation = param.annotation
                if isinstance(annotation, str):
                    # For string annotations, try to resolve from the implementation's module
                    module = inspect.getmodule(implementation)
                    if module and hasattr(module, annotation):
                        annotation = getattr(module, annotation)
                    else:
                        raise DependencyInjectionError(
                            f"Cannot resolve string annotation '{annotation}' for parameter {param.name}"
                        )

                dependency = self._resolve_dependency(annotation, scope, resolution_stack.copy())
                dependencies.append(dependency)

            # Create instance
            return implementation(*dependencies)

        finally:
            resolution_stack.discard(implementation)

    def _resolve_dependency(
        self, dependency_type: type, scope: ServiceScope | None, resolution_stack: set[type]
    ) -> Any:
        """Resolve a single dependency."""
        registration = self._get_registration(dependency_type)

        if registration.lifetime == ServiceLifetime.SINGLETON:
            return self._get_or_create_singleton(registration)
        elif registration.lifetime == ServiceLifetime.TRANSIENT:
            return self._create_instance_with_dependencies(registration.implementation, scope, resolution_stack)
        elif registration.lifetime == ServiceLifetime.SCOPED:
            if scope is None:
                raise DependencyInjectionError(f"Scoped service {dependency_type.__name__} requires a scope context")
            return scope.resolve(dependency_type)
        else:
            raise DependencyInjectionError(f"Unknown service lifetime: {registration.lifetime}")
