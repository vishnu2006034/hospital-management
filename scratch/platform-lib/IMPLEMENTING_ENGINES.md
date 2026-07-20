# Implementing an Engine — Developer Guide

Every engine in the platform (e.g. `hogc-crud-engine`, `hogc-iam-engine`)
has the same three-layer anatomy. This document tells you exactly which files to
read from `hogc-lib` and what you must write in your engine.

---

## Layers at a glance

```
hogc-lib (read-only contracts)
└── src/hogc/lib/
    ├── base.py                   ← shared base models (BaseDTO, BaseRequest, …)
    ├── kernel/                   ← infrastructure contracts (DI, events, errors, …)
    └── contracts/<domain>/       ← domain contracts for your engine

your-engine  (implementation)
└── src/hogc/engines/<domain>/
    ├── __init__.py
    ├── capability.py             ← implements the service ABCs from contracts
    ├── providers/
    │   ├── _base.py              ← optional internal provider ABC
    │   └── <backend>.py          ← concrete storage/provider implementation
    ├── schema.py                 ← ORM models / DB schema (if applicable)
    ├── events.py                 ← event name constants
    └── exceptions.py            ← engine-specific exceptions
```

---

## Step 1 — Read the right contract files

For your domain, open:

```
hogc-lib/src/hogc/lib/contracts/<domain>/
├── types.py      ← all enums you will use
├── models.py     ← DTOs returned to callers (e.g. RecordDTO, UserDTO)
├── requests.py   ← inbound request objects your service methods receive
├── responses.py  ← response wrappers your service methods must return
├── events.py     ← domain events you should publish after mutations
└── services.py   ← the ABCs you MUST implement  ← start here
```

> **Golden rule:** you only need to `import from hogc.lib.contracts.<domain>`
> and `hogc.lib.kernel`. Never import from another engine.

---

## Step 2 — Implement the service ABC

Open `contracts/<domain>/services.py`. It contains one or more `ABC` classes.
Create `capability.py` in your engine and subclass each one.

**Example — CRUD engine:**

```python
# src/hogc/engines/crud/capability.py
from __future__ import annotations

from hogc.lib.contracts.crud.services import RecordService
from hogc.lib.contracts.crud.requests import (
    CreateRecordRequest, GetRecordRequest, UpdateRecordRequest,
    DeleteRecordRequest, ListRecordsRequest, QueryRecordsRequest,
)
from hogc.lib.contracts.crud.responses import RecordResponse, RecordListResponse
from hogc.lib.contracts.crud.events import RecordCreatedEvent, RecordUpdatedEvent

from .providers._base import CRUDProvider
from hogc.lib.kernel.events import EventBus


class CRUDEngine(RecordService):
    def __init__(self, provider: CRUDProvider, bus: EventBus | None = None) -> None:
        self._provider = provider
        self._bus = bus

    def create_record(self, request: CreateRecordRequest) -> RecordResponse:
        record = self._provider.create(request)
        if self._bus:
            self._bus.publish(RecordCreatedEvent(
                aggregate_id=record.data.id,
                module_id=request.module_id,
            ))
        return RecordResponse(success=True, data=record)

    def get_record(self, request: GetRecordRequest) -> RecordResponse: ...
    def update_record(self, request: UpdateRecordRequest) -> RecordResponse: ...
    def delete_record(self, request: DeleteRecordRequest) -> RecordResponse: ...
    def list_records(self, request: ListRecordsRequest) -> RecordListResponse: ...
    def query_records(self, request: QueryRecordsRequest) -> RecordListResponse: ...
    # … implement every @abstractmethod or Python will raise TypeError at import
```

---

## Step 3 — Write the provider (if you need a storage backend)

The service ABC talks in contract types (DTOs, requests, responses). The provider
ABC (internal, not in hogc-lib) translates those to the actual database or API.

```python
# src/hogc/engines/crud/providers/_base.py
from abc import ABC, abstractmethod
from hogc.lib.contracts.crud.models import RecordDTO
from hogc.lib.contracts.crud.requests import CreateRecordRequest

class CRUDProvider(ABC):
    @abstractmethod
    def create(self, request: CreateRecordRequest) -> RecordDTO: ...
```

```python
# src/hogc/engines/crud/providers/postgres.py
from .._base import CRUDProvider

class PostgreSQLCRUDProvider(CRUDProvider):
    def __init__(self, session_factory) -> None:
        self._sf = session_factory

    def create(self, request: CreateRecordRequest) -> RecordDTO:
        # map request → ORM model → commit → map back to DTO
        ...
```

Keeping the provider separate means you can swap Postgres for MongoDB or an
in-memory mock without touching the service layer.

---

## Step 4 — Publish domain events

Events are defined in `hogc-lib/src/hogc/lib/contracts/<domain>/events.py`.
Import `DomainEvent` subclasses from there and publish via the kernel `EventBus`.

```python
from hogc.lib.contracts.crud.events import RecordCreatedEvent
from hogc.lib.kernel.events import EventBus

# inside your method, after the mutation succeeds:
if self._bus:
    self._bus.publish(RecordCreatedEvent(
        aggregate_id=record_id,
        module_id=module_id,
        data={"name": "Alice"},
    ))
```

All events extend `DomainEvent` (`hogc.lib.kernel.events`), which carries
`event_id`, `event_type`, `aggregate_id`, `aggregate_type`, `occurred_at`,
`tenant_id`, `org_id`, and a free-form `payload`.

---

## Step 5 — Use kernel infrastructure

| What you need | Import from |
|---|---|
| DI container | `hogc.lib.kernel.container.DIContainer` |
| Structured logging | `hogc.lib.kernel.logging.LoggerContract` |
| Standard errors | `hogc.lib.kernel.errors` (`NotFoundError`, `ValidationError`, …) |
| Event bus | `hogc.lib.kernel.events.EventBus` |
| Health checks | `hogc.lib.kernel.lifecycle.EngineLifecycle` |
| Config / secrets | `hogc.lib.kernel.config.ConfigProvider` |

```python
from hogc.lib.kernel.errors import NotFoundError, ValidationError

def get_record(self, request: GetRecordRequest) -> RecordResponse:
    row = self._provider.find(request.record_id)
    if row is None:
        raise NotFoundError(f"Record {request.record_id} not found")
    return RecordResponse(success=True, data=row)
```

---

## Step 6 — Register your implementation with `@provider`

Once your class implements a service ABC, decorate it with `@provider` so that
discoverability works automatically at boot — no manual registration is needed.
The `name` parameter is optional. If name is not specified (e.g. `None`), the lookup will automatically resolve it as the default (taking the one-and-only provider if there is one implementation, or the one explicitly marked as default/highest priority if there are 2+ implementations).

```python
# src/hogc/engines/crud/capability.py
from hogc.lib.kernel.registry import provider
from hogc.lib.contracts.crud.services import RecordService

@provider(
    RecordService,
    name="postgres",
    description="EAV storage over PostgreSQL via SQLAlchemy",
    priority=10,
    tags=["sql", "relational"],
)
class CRUDEngine(RecordService):
    ...
```

**Parameters**

| Parameter | Required | Description |
|---|---|---|
| `service` | ✅ | The service ABC this class implements |
| `name` | — | Optional short slug used in config to select this provider (e.g. `"postgres"`, `"mongo"`, `"in_memory"`) |
| `default` | — | Optional boolean. If True, this provider will be selected if name is not mentioned and 2+ implementations exist. |
| `description` | — | Human-readable text shown in diagnostics |
| `priority` | — | Higher wins when multiple providers match (default `0`) |
| `version` | — | Optional semver string for the implementation |
| `tags` | — | Free-form labels for filtering (e.g. `["sql", "relational"]`) |
| `metadata` | — | Arbitrary extra key/value pairs |

The decorator runs at **class-definition time** (import time) and immediately
registers the class in the global `ProviderRegistry`. If your class is not a
subclass of the declared service, a `TypeError` is raised at import, not at
runtime.

**How lookup works**

After importing all engine packages at startup, we query:

```python
from hogc.lib.kernel.registry import ProviderRegistry
from hogc.lib.contracts.crud.services import RecordService

# All providers for a service, sorted by descending priority:
providers = ProviderRegistry.get_providers(RecordService)

# Select by name (from config, name can be None/omitted):
Cls = ProviderRegistry.get_by_name(RecordService, config.crud.record_provider)
container.register_instance(RecordService, Cls(session_factory=sf))

# Highest-priority provider:
Cls = ProviderRegistry.get_default(RecordService)
```

> **Multiple providers for the same service** are fully supported — this is the
> expected pattern when you ship an in-memory stub alongside a real backend,
> or when multiple storage back-ends exist. Use `name` to distinguish them and
> `default=True` or `priority` to declare the preferred default.

---

## Step 7 — Raise engine-specific exceptions

For errors that are *specific* to your engine (e.g. column capacity exceeded),
declare them in `exceptions.py` and inherit from the right kernel base:

```python
# src/hogc/engines/crud/exceptions.py
from hogc.lib.kernel.errors import HogcError

class MaxColumnsExceededError(HogcError):
    status_code = 400
    def __init__(self, module_id: str) -> None:
        super().__init__(f"Module '{module_id}' has reached the 50-column limit")
```

---

## Reference — which file answers which question

| Question | File in hogc-lib |
|---|---|
| What enums exist for this domain? | `contracts/<domain>/types.py` |
| What does a DTO look like? | `contracts/<domain>/models.py` |
| What fields does a request carry? | `contracts/<domain>/requests.py` |
| What must my method return? | `contracts/<domain>/responses.py` |
| Which abstract methods must I implement? | `contracts/<domain>/services.py` |
| What events should I publish? | `contracts/<domain>/events.py` |
| How do I raise hogc-standard errors? | `kernel/errors.py` |
| How do I publish events? | `kernel/events.py` → `EventBus` |
| How do I read config / secrets? | `kernel/config.py` → `ConfigProvider` |
| Shared DTO base fields? | `base.py` → `BaseDTO`, `BaseRequest`, `BaseResponse` |
| How do I register my implementation? | `kernel/registry.py` → `@provider` decorator |
| How does enterprise discover providers? | `kernel/registry.py` → `ProviderRegistry` |

---

## Checklist before opening a PR

- [ ] Every `@abstractmethod` in the service ABC is implemented
- [ ] Methods return the exact response type declared in `responses.py`
- [ ] Domain events are published after every successful mutation
- [ ] Engine-specific errors subclass `HogcError` from `kernel/errors.py`
- [ ] Implementation class is decorated with `@provider(ServiceABC, name="...")` 
- [ ] No imports from `hogc.enterprise` or other engines
- [ ] Tests mock the provider, not the database
