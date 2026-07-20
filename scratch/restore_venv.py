import os

def run():
    target_dir = os.path.abspath("scratch/platform-lib/src/hogc/lib")
    
    # 1. Write kernel/context.py
    context_path = os.path.join(target_dir, "kernel/context.py")
    print(f"Writing {context_path}...")
    with open(context_path, "w", encoding="utf-8") as f:
        f.write('''"""
hogc.lib.kernel.context
============================
Execution context contracts.

Propagated via Python contextvars — asyncio-safe and thread-safe.
No implementation here. Context objects are immutable value objects.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import Field

from hogc.lib.base import PlatformModel, _utcnow, _new_id


# ---------------------------------------------------------------------------
# Context DTOs
# ---------------------------------------------------------------------------


class TenantContext(PlatformModel):
    """Identity of the tenant making the request."""

    tenant_id: str
    org_id: str
    schema_name: str = "public"
    plan: str | None = None
    features: list[str] = Field(default_factory=list)


class UserContext(PlatformModel):
    """Identity of the authenticated user."""

    user_id: str
    username: str
    email: str
    roles: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    is_service_account: bool = False
    impersonated_by: str | None = None


class ExecutionContext(PlatformModel):
    """Runtime execution metadata."""

    correlation_id: str = Field(default_factory=_new_id)
    trace_id: str = Field(default_factory=_new_id)
    request_id: str = Field(default_factory=_new_id)
    source: str | None = None
    engine: str | None = None
    operation: str | None = None
    started_at: datetime = Field(default_factory=_utcnow)
    attributes: dict[str, str] = Field(default_factory=dict)


class RequestContext(PlatformModel):
    """
    Full per-request context.

    Set once at the entry point (HTTP middleware, CLI, worker consumer).
    Read-only downstream via HogcContext.current().
    """

    tenant: TenantContext
    user: UserContext
    execution: ExecutionContext

    # Convenience accessors (denormalized for hot-path use)
    @property
    def tenant_id(self) -> str:
        return self.tenant.tenant_id

    @property
    def org_id(self) -> str:
        return self.tenant.org_id

    @property
    def user_id(self) -> str:
        return self.user.user_id

    @property
    def roles(self) -> list[str]:
        return self.user.roles

    @property
    def schema_name(self) -> str:
        return self.tenant.schema_name


class HogcContext(PlatformModel):
    """
    Top-level platform context envelope.

    Applications only interact with this; individual sub-contexts are
    accessible through named attributes.
    """

    request: RequestContext
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Context Provider Contract
# ---------------------------------------------------------------------------


class ContextProvider(ABC):
    """
    Contract for context propagation.

    Implementations bind/resolve context to the current async task
    or thread (e.g. via contextvars, thread-locals, or a WSGI environ).
    """

    @abstractmethod
    def set(self, ctx: HogcContext) -> Any:
        """Bind context; return a token usable with reset()."""

    @abstractmethod
    def current(self) -> HogcContext:
        """Return the currently bound context. Raise RuntimeError if unset."""

    @abstractmethod
    def reset(self, token: Any) -> None:
        """Restore the previous context."""

    @abstractmethod
    def current_or_none(self) -> HogcContext | None:
        """Return context or None if not set."""

import contextvars

_context_var = contextvars.ContextVar("hogc_context")

class ContextProviderImpl(ContextProvider):
    def set(self, ctx: HogcContext) -> Any:
        return _context_var.set(ctx)

    def current(self) -> HogcContext:
        ctx = _context_var.get(None)
        if ctx is None:
            raise RuntimeError("No active execution context found")
        return ctx

    def reset(self, token: Any) -> None:
        _context_var.reset(token)

    def current_or_none(self) -> HogcContext | None:
        return _context_var.get(None)

_global_provider: ContextProvider = ContextProviderImpl()

def get_context_provider() -> ContextProvider:
    return _global_provider

def set_context_provider(provider: ContextProvider) -> None:
    global _global_provider
    _global_provider = provider
''')

    # 2. Write kernel/container.py
    container_path = os.path.join(target_dir, "kernel/container.py")
    print(f"Writing {container_path}...")
    with open(container_path, "w", encoding="utf-8") as f:
        f.write('''from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from enum import Enum
from threading import RLock
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, get_type_hints

T = TypeVar("T")

class Scope(str, Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

class DIContainer(ABC, Generic[T]):
    @abstractmethod
    def register(
        self,
        interface: type[T],
        implementation: type[T] | None = None,
        *,
        factory: Callable[[], T] | None = None,
        scope: Scope = Scope.SINGLETON,
    ) -> None: ...

    @abstractmethod
    def register_instance(self, interface: type[T], instance: T) -> None: ...

    @abstractmethod
    def resolve(self, interface: type[T]) -> T: ...

    @abstractmethod
    def has(self, interface: type[T]) -> bool: ...

    @abstractmethod
    def create_scope(self) -> ScopedContainer: ...

    @abstractmethod
    def override(self, interface: type[T], instance: T) -> OverrideContext: ...


class ScopedContainer(DIContainer[Any]):
    @abstractmethod
    def close(self) -> None: ...

    def __enter__(self) -> ScopedContainer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class OverrideContext(ABC):
    @abstractmethod
    def __enter__(self) -> OverrideContext: ...

    @abstractmethod
    def __exit__(self, *args: Any) -> None: ...


from hogc.lib.kernel.errors import ContainerError

class _Provider:
    __slots__ = ("factory", "scope", "instance")

    def __init__(self, factory: Callable[[], Any], scope: Scope) -> None:
        self.factory = factory
        self.scope = scope
        self.instance: Any = None


class Container(DIContainer[Any]):
    def __init__(self, parent: Container | None = None) -> None:
        self._providers: Dict[type[Any], _Provider] = {}
        self._lock = RLock()
        self._parent = parent
        self._active_overrides: Dict[type[Any], Any] = {}
        self._child_scopes: List[ScopedContainerImpl] = []
        self._scoped_instances: Dict[type[Any], Any] = {}

    def register(
        self,
        interface: type[Any],
        implementation: type[Any] | None = None,
        *,
        factory: Callable[[], Any] | None = None,
        scope: Scope = Scope.SINGLETON,
    ) -> None:
        if implementation is None and factory is None:
            implementation = interface
            
        if factory is None:
            factory = self._build_factory(implementation)
            
        with self._lock:
            self._providers[interface] = _Provider(factory=factory, scope=scope)

    def register_instance(self, interface: type[Any], instance: Any) -> None:
        with self._lock:
            p = _Provider(factory=lambda: instance, scope=Scope.SINGLETON)
            p.instance = instance
            self._providers[interface] = p

    def has(self, interface: type[Any]) -> bool:
        with self._lock:
            if interface in self._active_overrides:
                return True
            if interface in self._providers:
                return True
            if self._parent:
                return self._parent.has(interface)
            return False

    def resolve(self, interface: type[Any]) -> Any:
        with self._lock:
            if interface in self._active_overrides:
                return self._active_overrides[interface]
                
            p = self._providers.get(interface)
            if p is not None:
                if p.scope == Scope.SINGLETON:
                    if p.instance is None:
                        p.instance = p.factory()
                    return p.instance
                elif p.scope == Scope.SCOPED:
                    scoped_container = self
                    while scoped_container and not isinstance(scoped_container, ScopedContainerImpl):
                        scoped_container = scoped_container._parent
                    if scoped_container:
                        if interface not in scoped_container._scoped_instances:
                            scoped_container._scoped_instances[interface] = p.factory()
                        return scoped_container._scoped_instances[interface]
                    else:
                        if interface not in self._scoped_instances:
                            self._scoped_instances[interface] = p.factory()
                        return self._scoped_instances[interface]
                else:
                    return p.factory()
            
            if self._parent:
                return self._parent.resolve(interface)
                
            from hogc.lib.kernel.registry import ProviderRegistry
            try:
                impl_cls = ProviderRegistry.resolve(interface)
                if impl_cls:
                    self.register(interface, impl_cls, scope=Scope.SINGLETON)
                    return self.resolve(interface)
            except Exception:
                pass
                
            raise ContainerError(
                f"No provider registered for '{getattr(interface, '__name__', interface)}'."
            )

    def create_scope(self) -> ScopedContainer:
        with self._lock:
            scope = ScopedContainerImpl(parent=self)
            self._child_scopes.append(scope)
            return scope

    def override(self, interface: type[Any], instance: Any) -> OverrideContext:
        return OverrideContextImpl(self, interface, instance)

    def _build_factory(self, cls: type[Any]) -> Callable[[], Any]:
        if not hasattr(cls, "__init__") or cls.__init__ is object.__init__:
            return lambda: cls()

        sig = inspect.signature(cls.__init__)
        try:
            hints = get_type_hints(cls.__init__)
        except Exception:
            hints = {}

        def factory() -> Any:
            kwargs: Dict[str, Any] = {}
            for name, _ in sig.parameters.items():
                if name == "self":
                    continue
                if name not in hints:
                    raise ContainerError(
                        f"Missing type hint for parameter '{name}' in {cls.__name__}. "
                        "All constructor parameters must be type-annotated for auto-wiring."
                    )
                kwargs[name] = self.resolve(hints[name])
            return cls(**kwargs)

        return factory


class ScopedContainerImpl(Container, ScopedContainer):
    def __init__(self, parent: Container) -> None:
        super().__init__(parent=parent)
        self._scoped_instances: Dict[type[Any], Any] = {}

    def close(self) -> None:
        with self._lock:
            self._scoped_instances.clear()
            if self._parent and self in self._parent._child_scopes:
                self._parent._child_scopes.remove(self)


class OverrideContextImpl(OverrideContext):
    def __init__(self, container: Container, interface: type[Any], instance: Any) -> None:
        self._container = container
        self._interface = interface
        self._instance = instance
        self._old_override = None
        self._had_old_override = False

    def __enter__(self) -> OverrideContext:
        with self._container._lock:
            if self._interface in self._container._active_overrides:
                self._had_old_override = True
                self._old_override = self._container._active_overrides[self._interface]
            self._container._active_overrides[self._interface] = self._instance
        return self

    def __exit__(self, *args: Any) -> None:
        with self._container._lock:
            if self._had_old_override:
                self._container._active_overrides[self._interface] = self._old_override
            else:
                self._container._active_overrides.pop(self._interface, None)


_global_container: Container = Container()

def get_container() -> Container:
    return _global_container

def set_container(container: Container) -> None:
    global _global_container
    _global_container = container

def resolve(interface: type[T]) -> T:
    return get_container().resolve(interface)

def register(
    interface: type[T],
    implementation: type[T] | None = None,
    *,
    factory: Callable[[], T] | None = None,
    scope: Scope = Scope.SINGLETON,
) -> None:
    get_container().register(interface, implementation, factory=factory, scope=scope)

def register_instance(interface: type[T], instance: T) -> None:
    get_container().register_instance(interface, instance)


class ServiceFacade:
    def __init__(self, interface: type[Any]) -> None:
        self._interface = interface

    def __get__(self, instance: Any, owner: Any) -> Any:
        return resolve(self._interface)
''')

    # 3. Write kernel/lifecycle.py
    lifecycle_path = os.path.join(target_dir, "kernel/lifecycle.py")
    print(f"Writing {lifecycle_path}...")
    with open(lifecycle_path, "w", encoding="utf-8") as f:
        f.write('''"""
hogc.lib.kernel.lifecycle
==============================
Engine lifecycle contracts.
"""
from __future__ import annotations

import functools
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Coroutine, List, Tuple
from pydantic import Field

log = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class EngineState(str, Enum):
    UNINITIALIZED = "uninitialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"

from hogc.lib.base import PlatformModel

class HealthCheckResult(PlatformModel):
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float | None = None
    details: dict[str, Any] = Field(default_factory=dict)

class EngineInfo(PlatformModel):
    name: str
    version: str
    description: str = ""
    provider: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

SyncHook = Callable[[], None]
AsyncHook = Callable[[], Coroutine[Any, Any, None]]
AnyHook = SyncHook | AsyncHook

class StartupHook(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    def priority(self) -> int: return 50
    @abstractmethod
    def execute(self) -> None: ...

class ShutdownHook(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    def priority(self) -> int: return 50
    @abstractmethod
    def execute(self) -> None: ...

class HealthCheck(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    def critical(self) -> bool: return True
    @abstractmethod
    def check(self) -> HealthCheckResult: ...

class EngineLifecycle(ABC):
    @property
    @abstractmethod
    def info(self) -> EngineInfo: ...
    @property
    def state(self) -> EngineState: return EngineState.UNINITIALIZED
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def health_check(self) -> list[HealthCheckResult]: ...

_startup_hooks: List[Tuple[int, Callable]] = []
_shutdown_hooks: List[Tuple[int, Callable]] = []

def on_startup(*, priority: int = 50) -> Callable:
    def decorator(fn: Callable) -> Callable:
        _startup_hooks.append((priority, fn))
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any: return fn(*args, **kwargs)
        return wrapper
    return decorator

def on_shutdown(*, priority: int = 50) -> Callable:
    def decorator(fn: Callable) -> Callable:
        _shutdown_hooks.append((priority, fn))
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any: return fn(*args, **kwargs)
        return wrapper
    return decorator

class LifecycleManager:
    def __init__(self) -> None:
        self._startup: List[Tuple[int, Callable]] = []
        self._shutdown: List[Tuple[int, Callable]] = []
    def add_startup(self, fn: Callable, *, priority: int = 50) -> None: self._startup.append((priority, fn))
    def add_shutdown(self, fn: Callable, *, priority: int = 50) -> None: self._shutdown.append((priority, fn))
    def run_startup_hooks(self) -> None:
        hooks = sorted(_startup_hooks + self._startup, key=lambda t: t[0])
        for _, fn in hooks: fn()
    def run_shutdown_hooks(self) -> None:
        hooks = sorted(_shutdown_hooks + self._shutdown, key=lambda t: t[0])
        for _, fn in hooks:
            try: fn()
            except Exception: log.exception("Shutdown hook failed")
''')

    # 4. Write kernel/logging.py
    logging_path = os.path.join(target_dir, "kernel/logging.py")
    print(f"Writing {logging_path}...")
    with open(logging_path, "w", encoding="utf-8") as f:
        f.write('''"""
hogc.lib.kernel.logging
=============================
Structured logging and correlation contracts.
"""
from __future__ import annotations

import contextvars
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class CorrelationContext(ABC):
    @property
    @abstractmethod
    def correlation_id(self) -> str: ...
    @property
    @abstractmethod
    def trace_id(self) -> str: ...
    @property
    @abstractmethod
    def request_id(self) -> str: ...
    @abstractmethod
    def set(self, correlation_id: str, trace_id: str, request_id: str) -> Any: ...
    @abstractmethod
    def reset(self, token: Any) -> None: ...

class LoggerContract(ABC):
    @abstractmethod
    def debug(self, message: str, **fields: Any) -> None: ...
    @abstractmethod
    def info(self, message: str, **fields: Any) -> None: ...
    @abstractmethod
    def warning(self, message: str, **fields: Any) -> None: ...
    @abstractmethod
    def error(self, message: str, **fields: Any) -> None: ...
    @abstractmethod
    def critical(self, message: str, **fields: Any) -> None: ...
    @abstractmethod
    def bind(self, **fields: Any) -> "LoggerContract": ...

class AuditLoggerContract(ABC):
    @abstractmethod
    def log_access(self, *, actor_id: str, tenant_id: str, org_id: str, action: str, resource_type: str, resource_id: str | None = None, outcome: str, ip_address: str | None = None, metadata: dict[str, Any] | None = None) -> str: ...
    @abstractmethod
    def log_change(self, *, actor_id: str, tenant_id: str, org_id: str, action: str, resource_type: str, resource_id: str, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None) -> str: ...
    @abstractmethod
    def log_event(self, *, actor_id: str, tenant_id: str, org_id: str, event_type: str, description: str, severity: str = "info", metadata: dict[str, Any] | None = None) -> str: ...

_correlation_id_var = contextvars.ContextVar("_correlation_id", default="-")
_trace_id_var = contextvars.ContextVar("_trace_id", default="-")
_request_id_var = contextvars.ContextVar("_request_id", default="-")

class CorrelationContextImpl(CorrelationContext):
    @property
    def correlation_id(self) -> str: return _correlation_id_var.get()
    @property
    def trace_id(self) -> str: return _trace_id_var.get()
    @property
    def request_id(self) -> str: return _request_id_var.get()
    def set(self, correlation_id: str, trace_id: str, request_id: str) -> Any:
        t1 = _correlation_id_var.set(correlation_id)
        t2 = _trace_id_var.set(trace_id)
        t3 = _request_id_var.set(request_id)
        return (t1, t2, t3)
    def reset(self, token: Any) -> None:
        t1, t2, t3 = token
        _correlation_id_var.reset(t1)
        _trace_id_var.reset(t2)
        _request_id_var.reset(t3)

_global_correlation_context: CorrelationContext = CorrelationContextImpl()

def get_correlation_context() -> CorrelationContext: return _global_correlation_context
def set_correlation_context(context: CorrelationContext) -> None:
    global _global_correlation_context
    _global_correlation_context = context
''')

    # 5. Write kernel/events.py
    events_path = os.path.join(target_dir, "kernel/events.py")
    print(f"Writing {events_path}...")
    with open(events_path, "w", encoding="utf-8") as f:
        f.write('''"""
hogc.lib.kernel.events
============================
Platform event system contracts.
"""
from __future__ import annotations

import fnmatch
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Any, Callable, Generic, TypeVar
from uuid import uuid4
from pydantic import Field

from hogc.lib.base import PlatformModel, _utcnow, _new_id

log = logging.getLogger(__name__)

class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class DeliveryMode(str, Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"

class Event(PlatformModel):
    event_id: str = Field(default_factory=_new_id)
    event_type: str
    event_version: str = "1.0"
    occurred_at: datetime = Field(default_factory=_utcnow)
    tenant_id: str
    org_id: str
    source: str
    correlation_id: str = Field(default_factory=_new_id)
    causation_id: str | None = None
    priority: EventPriority = EventPriority.NORMAL
    payload: dict[str, Any] = Field(default_factory=dict)

class DomainEvent(Event):
    aggregate_type: str
    aggregate_id: str

class IntegrationEvent(Event):
    topic: str
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    schema_version: str = "1.0"
    routing_key: str | None = None

class DeadLetterEvent(PlatformModel):
    original_event: Event
    dead_letter_at: datetime = Field(default_factory=_utcnow)
    retry_count: int = 0
    last_error: str = ""
    queue: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)

E = TypeVar("E", bound=Event)
EventHandler = Callable[[E], None]

class EventPublisher(ABC, Generic[E]):
    @abstractmethod
    def publish(self, event: E) -> None: ...
    @abstractmethod
    def publish_batch(self, events: list[E]) -> None: ...

class EventSubscriber(ABC, Generic[E]):
    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler[E]) -> str: ...
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> None: ...

class EventBus(EventPublisher[E], EventSubscriber[E], Generic[E]):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def replay(self, event_type: str, *, from_timestamp: datetime | None = None, tenant_id: str | None = None, limit: int = 1000) -> list[E]: ...

class InMemoryEventBus(EventBus[Event]):
    def __init__(self) -> None:
        self._handlers: dict[str, dict[str, EventHandler[Event]]] = {}
        self._lock = RLock()
        self._history: list[Event] = []
        self._started = False
    def start(self) -> None: self._started = True
    def stop(self) -> None:
        self._started = False
        with self._lock: self._handlers.clear()
    def publish(self, event: Event) -> None:
        with self._lock:
            self._history.append(event)
            to_invoke = []
            for pattern, handlers_dict in self._handlers.items():
                if fnmatch.fnmatch(event.event_type, pattern): to_invoke.extend(handlers_dict.values())
        for handler in to_invoke:
            try: handler(event)
            except Exception: log.exception("Error in event handler")
    def publish_batch(self, events: list[Event]) -> None:
        for event in events: self.publish(event)
    def subscribe(self, event_type: str, handler: EventHandler[Event]) -> str:
        sub_id = uuid4().hex
        with self._lock:
            if event_type not in self._handlers: self._handlers[event_type] = {}
            self._handlers[event_type][sub_id] = handler
        return sub_id
    def unsubscribe(self, subscription_id: str) -> None:
        with self._lock:
            for event_type, handlers_dict in list(self._handlers.items()):
                if subscription_id in handlers_dict:
                    del handlers_dict[subscription_id]
                    if not handlers_dict: del self._handlers[event_type]
                    break
    def replay(self, event_type: str, *, from_timestamp: datetime | None = None, tenant_id: str | None = None, limit: int = 1000) -> list[Event]:
        with self._lock:
            results = []
            for event in self._history:
                if fnmatch.fnmatch(event.event_type, event_type):
                    if from_timestamp and event.occurred_at < from_timestamp: continue
                    if tenant_id and event.tenant_id != tenant_id: continue
                    results.append(event)
                    if len(results) >= limit: break
            return results

from hogc.lib.kernel.container import ServiceFacade
HEventBus: EventBus = ServiceFacade(EventBus)  # type: ignore[assignment]
''')

    # 6. Write kernel/database.py and kernel/cache.py stubs
    db_path = os.path.join(target_dir, "kernel/database.py")
    print(f"Writing {db_path}...")
    with open(db_path, "w", encoding="utf-8") as f:
        f.write("# database stub\nSessionFactory = None\nUnitOfWork = None\n")

    cache_path = os.path.join(target_dir, "kernel/cache.py")
    print(f"Writing {cache_path}...")
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write("# cache stub\nCacheProvider = None\nNamespacedCache = None\n")

    # 7. Write contracts/policy/decorators.py
    decorators_path = os.path.join(target_dir, "contracts/policy/decorators.py")
    print(f"Writing {decorators_path}...")
    os.makedirs(os.path.dirname(decorators_path), exist_ok=True)
    with open(decorators_path, "w", encoding="utf-8") as f:
        f.write('''from __future__ import annotations

from functools import wraps
from typing import Any, Callable
from hogc.lib.contracts.policy.models import PolicyIntent, PolicyResource
from hogc.lib.contracts.policy.requests import EvaluateRequest
from hogc.lib.contracts.policy.services import PolicyService
from hogc.lib.kernel.container import resolve
from hogc.lib.kernel.context import get_context_provider
from hogc.lib.kernel.errors import AuthorizationError
from hogc.lib.kernel.registry import ProviderRegistry

def enforce_policy(
    action: str,
    resource_type: str,
    resource_id_param: str | None = None,
    context_keys: list[str] | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            policy_service = None
            try: policy_service = resolve(PolicyService)
            except Exception:
                try: policy_service = ProviderRegistry.resolve(PolicyService)
                except Exception: pass
            if not policy_service: raise AuthorizationError("PolicyService not resolved")
            provider_ctx = get_context_provider()
            platform_ctx = provider_ctx.current()
            if not platform_ctx: raise AuthorizationError("No active context found")
            resource_id = None
            if resource_id_param:
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                resource_id = bound_args.arguments.get(resource_id_param)
            context_attrs = {}
            if context_keys:
                import inspect
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                for key in context_keys:
                    if key in bound_args.arguments: context_attrs[key] = bound_args.arguments[key]
            resource = PolicyResource(type=resource_type, id=resource_id)
            intent = PolicyIntent(action=action, resource=resource, context=context_attrs)
            from hogc.lib.base import RequestContext as BaseRequestContext
            req_ctx = platform_ctx.request
            base_req_ctx = BaseRequestContext(
                tenant_id=req_ctx.tenant.tenant_id,
                org_id=req_ctx.tenant.org_id,
                user_id=req_ctx.user.user_id,
                roles=req_ctx.user.roles,
                schema_name=req_ctx.tenant.schema_name,
                source=req_ctx.execution.source,
                attributes=req_ctx.execution.attributes
            )
            request = EvaluateRequest(context=base_req_ctx, intent=intent)
            response = policy_service.evaluate(request)
            if not response or not response.decision or not response.decision.allowed:
                raise AuthorizationError("Access denied by policy evaluation")
            return func(*args, **kwargs)
        return wrapper
    return decorator
''')

    # 8. Write facade.py
    facade_path = os.path.join(target_dir, "facade.py")
    print(f"Writing {facade_path}...")
    with open(facade_path, "w", encoding="utf-8") as f:
        f.write('''from __future__ import annotations

from typing import Any
from hogc.lib.kernel.container import resolve

class HOGCFacade:
    @property
    def _service_mappings(self) -> dict:
        from hogc.lib.contracts.policy.services import PolicyService
        from hogc.lib.contracts.crud.services.record import RecordService
        from hogc.lib.kernel.config import ConfigProvider, SecretProvider, FeatureFlagProvider
        return {
            "policy": PolicyService,
            "policy_service": PolicyService,
            "policyservice": PolicyService,
            "record": RecordService,
            "record_service": RecordService,
            "recordservice": RecordService,
            "config": ConfigProvider,
            "config_provider": ConfigProvider,
            "configprovider": ConfigProvider,
            "secret": SecretProvider,
            "secret_provider": SecretProvider,
            "secretprovider": SecretProvider,
            "feature_flag": FeatureFlagProvider,
            "feature_flag_provider": FeatureFlagProvider,
            "featureflagprovider": FeatureFlagProvider,
        }

    def __getattr__(self, name: str) -> Any:
        norm_name = name.lower().replace("_", "")
        mappings = self._service_mappings
        for key, service_cls in mappings.items():
            if key.lower().replace("_", "") == norm_name: return resolve(service_cls)
        for service_cls in set(mappings.values()):
            try:
                service = resolve(service_cls)
                if hasattr(service, name): return getattr(service, name)
            except Exception: continue
        raise AttributeError(f"HOGC facade has no attribute or resolved service method '{name}'")

HOGC = HOGCFacade()
''')

    # 9. Write kernel/__init__.py
    kernel_init_path = os.path.join(target_dir, "kernel/__init__.py")
    print(f"Writing {kernel_init_path}...")
    with open(kernel_init_path, "w", encoding="utf-8") as f:
        f.write('''"""hogc.lib.kernel package."""
from hogc.lib.kernel.context import (
    TenantContext,
    UserContext,
    ExecutionContext,
    RequestContext,
    HogcContext,
    ContextProvider,
    ContextProviderImpl,
    get_context_provider,
    set_context_provider,
)
from hogc.lib.kernel.lifecycle import (
    HealthStatus,
    EngineState,
    HealthCheckResult,
    EngineInfo,
    StartupHook,
    ShutdownHook,
    HealthCheck,
    EngineLifecycle,
    LifecycleManager,
    on_startup,
    on_shutdown,
)
from hogc.lib.kernel.registry import (
    RegistryEntry,
    CapabilityRegistry,
    ServiceRegistry,
    ProviderMeta,
    ProviderRegistry,
    provider,
)
from hogc.lib.kernel.container import (
    Scope,
    DIContainer,
    ScopedContainer,
    OverrideContext,
    Container,
    get_container,
    set_container,
    resolve,
    register,
    register_instance,
    ServiceFacade,
)
from hogc.lib.kernel.events import (
    EventPriority,
    DeliveryMode,
    Event,
    DomainEvent,
    IntegrationEvent,
    DeadLetterEvent,
    EventPublisher,
    EventSubscriber,
    EventBus,
    InMemoryEventBus,
    HEventBus,
)
from hogc.lib.kernel.logging import (
    LogLevel,
    CorrelationContext,
    LoggerContract,
    AuditLoggerContract,
    CorrelationContextImpl,
    get_correlation_context,
    set_correlation_context,
)
from hogc.lib.kernel.errors import (
    HogcError,
    ValidationError,
    NotFoundError,
    AlreadyExistsError,
    ConflictError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ServiceUnavailableError,
    ProviderError,
    ConfigurationError,
    CapabilityNotRegisteredError,
    ServiceNotRegisteredError,
    ContainerError,
)
from hogc.lib.kernel.config import (
    SecretRotationStatus,
    FeatureFlagVariant,
    SecretMetadata,
    FeatureFlag,
    ConfigProvider,
    SecretProvider,
    FeatureFlagProvider,
)
from hogc.lib.kernel.database import SessionFactory, UnitOfWork
from hogc.lib.kernel.cache import CacheProvider, NamespacedCache

__all__ = [
    "TenantContext", "UserContext", "ExecutionContext", "RequestContext",
    "HogcContext", "ContextProvider", "ContextProviderImpl",
    "get_context_provider", "set_context_provider",
    "HealthStatus", "EngineState", "HealthCheckResult", "EngineInfo",
    "StartupHook", "ShutdownHook", "HealthCheck", "EngineLifecycle",
    "LifecycleManager", "on_startup", "on_shutdown",
    "RegistryEntry", "CapabilityRegistry", "ServiceRegistry",
    "ProviderMeta", "ProviderRegistry", "provider",
    "Scope", "DIContainer", "ScopedContainer", "OverrideContext",
    "Container", "get_container", "set_container", "resolve", "register", "register_instance", "ServiceFacade",
    "EventPriority", "DeliveryMode", "Event", "DomainEvent", "IntegrationEvent",
    "DeadLetterEvent", "EventPublisher", "EventSubscriber", "EventBus",
    "InMemoryEventBus", "HEventBus",
    "LogLevel", "CorrelationContext", "LoggerContract", "AuditLoggerContract",
    "CorrelationContextImpl", "get_correlation_context", "set_correlation_context",
    "HogcError", "ValidationError", "NotFoundError", "AlreadyExistsError",
    "ConflictError", "AuthenticationError", "AuthorizationError", "RateLimitError",
    "ServiceUnavailableError", "ProviderError", "ConfigurationError",
    "CapabilityNotRegisteredError", "ServiceNotRegisteredError", "ContainerError",
    "SecretRotationStatus", "FeatureFlagVariant", "SecretMetadata", "FeatureFlag",
    "ConfigProvider", "SecretProvider", "FeatureFlagProvider",
    "SessionFactory", "UnitOfWork",
    "CacheProvider", "NamespacedCache",
]
''')

    # 10. Write __init__.py in hogc/lib/
    lib_init_path = os.path.join(target_dir, "__init__.py")
    print(f"Writing {lib_init_path}...")
    with open(lib_init_path, "w", encoding="utf-8") as f:
        f.write('''"""hogc-lib: The stable kernel and complete contract layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .kernel.container import Container, Scope, resolve, register, register_instance, ServiceFacade
from .kernel.errors import (
    HogcError,
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ContainerError,
)
from .kernel.lifecycle import LifecycleManager, on_startup, on_shutdown
from .kernel.context import (
    TenantContext,
    UserContext,
    ExecutionContext,
    RequestContext,
    HogcContext,
    get_context_provider,
)

@dataclass(frozen=True)
class Context:
    tenant_id: str
    user_id: str
    roles: List[str]
    schema_name: str = "public"
    request_id: Optional[str] = None
    source: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None

    @staticmethod
    def set(*, tenant_id: str, user_id: str, roles: List[str], schema_name: str = "public", request_id: Optional[str] = None, source: Optional[str] = None, attributes: Optional[Dict[str, str]] = None) -> Any:
        tenant = TenantContext(tenant_id=tenant_id, org_id=tenant_id, schema_name=schema_name)
        user = UserContext(user_id=user_id, username=user_id, email=f"{user_id}@example.com", roles=roles)
        execution = ExecutionContext(request_id=request_id or "-", source=source, attributes=attributes or {})
        req_ctx = RequestContext(tenant=tenant, user=user, execution=execution)
        platform_ctx = HogcContext(request=req_ctx)
        return get_context_provider().set(platform_ctx)

    @staticmethod
    def current() -> Context:
        ctx = get_context_provider().current()
        return Context(
            tenant_id=ctx.request.tenant_id,
            user_id=ctx.request.user_id,
            roles=ctx.request.roles,
            schema_name=ctx.request.schema_name,
            request_id=ctx.request.execution.request_id,
            source=ctx.request.execution.source,
            attributes=ctx.request.execution.attributes,
        )

    @staticmethod
    def reset(token: Any) -> None:
        get_context_provider().reset(token)

    def is_system(self) -> bool: return self.source == "system"
    def has_role(self, role: str) -> bool: return role in self.roles

from .base import (
    EntityStatus,
    PlatformModel,
    BaseDTO,
    RequestContext as BaseRequestContext,
    BaseRequest,
    BaseResponse,
    DataResponse,
    PagedResponse,
    BulkResponse,
)
from .facade import HOGC
from . import kernel
from . import contracts

__all__ = [
    "Container", "Scope", "resolve", "register", "register_instance", "ServiceFacade",
    "ContainerError",
    "Context",
    "HogcError", "NotFoundError", "AlreadyExistsError",
    "ValidationError", "AuthenticationError", "AuthorizationError", "ConflictError",
    "LifecycleManager", "on_startup", "on_shutdown",
    "EntityStatus", "PlatformModel", "BaseDTO",
    "BaseRequestContext", "BaseRequest", "BaseResponse",
    "DataResponse", "PagedResponse", "BulkResponse",
    "HOGC",
    "kernel",
    "contracts",
]
''')
    print("Restore complete!")

if __name__ == "__main__":
    run()
