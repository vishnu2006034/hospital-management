# hogc-lib

The stable kernel of the HOGC platform. Contains all shared abstractions —
domain contracts, kernel infrastructure, types, errors, DI container, context,
lifecycle, events, structured logging, async database sessions, and cache
contracts. Every other hogc package depends on this; nothing here depends
on any engine.

---

## What it contains

### Kernel (`hogc.lib.kernel`)

| Module | Exports |
|--------|---------|
| `kernel.context` | `TenantContext`, `UserContext`, `ExecutionContext`, `RequestContext`, `HogcContext`, `ContextProvider` |
| `kernel.container` | `DIContainer`, `ScopedContainer`, `Scope`, `OverrideContext` |
| `kernel.registry` | `ProviderRegistry`, `@provider` decorator, `ProviderMeta`, `CapabilityRegistry`, `ServiceRegistry` |
| `kernel.events` | `EventBus`, `EventPublisher`, `EventSubscriber`, `DomainEvent`, `IntegrationEvent`, `DeadLetterEvent` |
| `kernel.lifecycle` | `EngineLifecycle`, `HealthCheck`, `StartupHook`, `ShutdownHook`, `HealthCheckResult`, `EngineInfo` |
| `kernel.logging` | `LoggerContract`, `AuditLoggerContract`, `CorrelationContext`, `LogLevel` |
| `kernel.errors` | `HogcError`, `NotFoundError`, `ValidationError`, `AlreadyExistsError`, `ConflictError`, `AuthenticationError`, `AuthorizationError`, `RateLimitError`, `ServiceUnavailableError`, `ProviderError`, `ConfigurationError` |
| `kernel.config` | `ConfigProvider`, `SecretProvider`, `FeatureFlagProvider`, `FeatureFlag`, `SecretMetadata` |
| `kernel.database` | `SessionFactory`, `UnitOfWork` — async SQLAlchemy session contracts |
| `kernel.cache` | `CacheProvider`, `NamespacedCache` — async cache contracts (Redis / Memcached / in-memory) |

### Domain Contracts (`hogc.lib.contracts`)

One sub-package per domain. Each exposes `types`, `models`, `requests`, `responses`, `events`, and `services` (ABCs).

| Domain | Service ABCs |
|--------|-------------|
| `contracts.crud` | `RecordService`, `ModuleService`, `FieldService`, `LayoutService`, `PicklistService`, `RelatedRecordService`, `ConversionService`, `ConversionMappingService`, `ImportExportService` |
| `contracts.iam` | `UserService`, `RoleService`, `OrgService`, `AuthService` |
| `contracts.policy` | `PolicyService` |
| `contracts.audit` | `AuditService` |
| `contracts.ai` | `AIService` |
| `contracts.automation` | `AutomationService` |
| `contracts.events` | `EventService` |
| `contracts.messaging` | `MessagingService` |
| `contracts.notification` | `NotificationService` |
| `contracts.reporting` | `ReportingService` |
| `contracts.search` | `SearchService` |
| `contracts.storage` | `StorageService` |
| `contracts.task` | `TaskService` |
| `contracts.waf` | `WAFService` |

### Shared Base (`hogc.lib.base`, `hogc.lib.database`, `hogc.lib.types`)

- `base.py` — `BaseDTO`, `BaseRequest`, `BulkResponse`, and other shared Pydantic models
- `database.py` — shared SQLAlchemy `DeclarativeBase` for ORM models in engines
- `types/` — shared domain types: `records`, `auth`, `audit`, `policy`, `schema`

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/HOGC-IN/hogc-lib.git
cd hogc-lib
```

### 2. Create a virtual environment

```bash
uv venv --python /opt/homebrew/bin/python3.14 .venv
source .venv/bin/activate
```

> **macOS note:** if you see `Python executable does not support -I flag`,
> uv picked up system Python 2.7. Always pass `--python` explicitly.
> If you see `interpreter is externally managed`, you skipped the venv step.

### 3. Install in editable mode with dev dependencies

```bash
uv pip install -e ".[dev]"
```

### 4. Run the tests

```bash
pytest
```

### 5. Lint and type-check

```bash
ruff check src/
mypy src/
```

---

## Project structure

```
src/hogc/lib/
├── base.py                    # Shared Pydantic base models (BaseDTO, BaseRequest, …)
├── database.py                # Shared SQLAlchemy DeclarativeBase
├── context.py                 # Per-request context (legacy shim → kernel.context)
├── errors.py                  # Exception hierarchy (legacy shim → kernel.errors)
├── lifecycle.py               # Startup/shutdown hooks (legacy shim → kernel.lifecycle)
├── logging.py                 # Structured logging (legacy shim → kernel.logging)
├── container.py               # DI container (legacy shim → kernel.container)
├── types/                     # Shared domain types
│   ├── records.py
│   ├── auth.py
│   ├── audit.py
│   ├── policy.py
│   └── schema.py
├── kernel/                    # Infrastructure contracts (import from here in engines)
│   ├── cache.py               # CacheProvider, NamespacedCache
│   ├── config.py              # ConfigProvider, SecretProvider, FeatureFlagProvider
│   ├── container.py           # DIContainer, ScopedContainer
│   ├── context.py             # HogcContext, ContextProvider
│   ├── database.py            # SessionFactory, UnitOfWork
│   ├── errors.py              # Full exception hierarchy
│   ├── events.py              # EventBus, DomainEvent, IntegrationEvent
│   ├── lifecycle.py           # EngineLifecycle, HealthCheck
│   ├── logging.py             # LoggerContract, AuditLoggerContract
│   └── registry.py            # @provider, ProviderRegistry
├── contracts/                 # Domain service ABCs (one package per domain)
│   ├── ai/
│   ├── audit/
│   ├── automation/
│   ├── crud/
│   ├── events/
│   ├── iam/
│   ├── messaging/
│   ├── notification/
│   ├── policy/
│   ├── reporting/
│   ├── search/
│   ├── storage/
│   ├── task/
│   └── waf/
└── events/
    └── bus.py                 # InMemoryEventBus (for testing / local dev)
```

---

The primary entry point for developers is the unified `HOGC` facade, exposing all active engines as domain namespaces:

```python
from hogc.lib import HOGC
from hogc.lib.contracts.crud.requests import CreateRecordRequest

# 1. Access domain services directly
record_response = HOGC.record.create_record(CreateRecordRequest(module_id="mod_123", data={}))

# 2. Access infrastructure services
db_password = HOGC.secret.get_secret("db.password")
HOGC.cache.set("my_key", "my_value")
```

For engine authors, define capability implementations by decorating them with `@provider`:

```python
from hogc.lib.kernel.registry import provider
from hogc.lib.contracts.crud.services import RecordService

@provider(RecordService, name="postgres", priority=10, tags=["sql"])
class CRUDEngine(RecordService):
    ...
```

See [IMPLEMENTING_ENGINES.md](IMPLEMENTING_ENGINES.md) for the full step-by-step guide, and [usage_examples.md](usage_examples.md) for self-contained usage code examples.

---

## What it does NOT contain

- No engine implementations (those live in `hogc-*-engine` packages)
- No SQLAlchemy ORM models (only the shared `DeclarativeBase`)
- No concrete cache or database clients (Redis, psycopg, etc. — those live in `hogc-infra`)
- No third-party auth libs (bcrypt, PyJWT, etc.)
