# Usage Examples for hogc-lib

This document provides comprehensive, concrete code examples showing how to use the core components and contracts of `hogc-lib` in your engines.

---

The unified `HOGC` facade is the primary entry point for developers. It groups all active contracts as domain properties:

```python
from hogc.lib import HOGC
from hogc.lib.contracts.crud.requests import GetRecordRequest

# 1. Access domain services through clean property groups
record = HOGC.record.get_record(GetRecordRequest(record_id="rec_123"))

# 2. Access infrastructure services
db_password = HOGC.secret.get_secret("db.password")
is_v2_enabled = HOGC.feature_flag.is_enabled("new-ui-v2")
max_limit = HOGC.config.get_int("app.max_limit")
```

---

## 2. Dependency Injection (`hogc.lib.kernel.container`)

Register capability interfaces, wire them up in classes, and manage child lifecycles:

```python
from hogc.lib.kernel.container import Scope, resolve, register, ServiceFacade, get_container
from hogc.lib.kernel.errors import ContainerError

# 1. Interfaces
class StorageClient:
    pass

class FileService:
    def __init__(self, client: StorageClient) -> None:
        self.client = client
    def download(self, doc_id: str) -> bytes:
        return b"file content"

# 2. Setup Container using Facade functions
# Register transient or singleton dependencies globally
# NOTE: Manual registration is optional if the implementation is decorated with @provider!
register(StorageClient, factory=lambda: StorageClient(), scope=Scope.TRANSIENT)
register(FileService, FileService, scope=Scope.SINGLETON)

# 3. Create a static Proxy Facade wrapper (HFileService)
# Giving it a type annotation guarantees full IDE autocomplete / type-checking.
HFileService: FileService = ServiceFacade(FileService)  # type: ignore[assignment]

# 4. Use it directly! Under the hood, it resolves FileService on-demand.
content = HFileService.download("doc_123")
assert content == b"file content"

# 5. Scoped Child Containers (e.g. isolated per request)
container = get_container()
scope = container.create_scope()
# Registers a scoped dependency valid only inside this scope
class RequestTracker:
    pass

scope.register(RequestTracker, RequestTracker, scope=Scope.SCOPED)
tracker = scope.resolve(RequestTracker)
scope.close()

# 5. Overriding Registrations for Testing
mock_client = StorageClient()
with container.override(StorageClient, mock_client):
    assert container.resolve(StorageClient) is mock_client
```

---

## 3. Execution Context (`hogc.lib.kernel.context`)

Store and retrieve multi-tenant request and user identity information safely across async boundaries:

```python
from hogc.lib.kernel.context import (
    TenantContext,
    UserContext,
    ExecutionContext,
    RequestContext,
    HogcContext,
    get_context_provider,
)

provider = get_context_provider()

# 1. Construct Request identity
tenant = TenantContext(tenant_id="tenant_abc", org_id="org_123", schema_name="tenant_abc_schema")
user = UserContext(user_id="usr_007", username="bond", email="bond@mi6.gov", roles=["agent", "admin"])
exec_ctx = ExecutionContext(source="api_gateway", operation="DownloadFiles")

req_ctx = RequestContext(tenant=tenant, user=user, execution=exec_ctx)
platform_ctx = HogcContext(request=req_ctx)

# 2. Bind context (e.g., inside an API middleware)
token = provider.set(platform_ctx)

# 3. Access current context downstream (without passing it as a function parameter)
try:
    current_ctx = provider.current()
    print(f"Active Tenant: {current_ctx.request.tenant_id}")
    print(f"Current User: {current_ctx.request.user_id}")
    print(f"Current User Roles: {current_ctx.request.roles}")
finally:
    # 4. Reset context on request completion
    provider.reset(token)
```

---

## 4. Event Bus & Publishing (`hogc.lib.kernel.events`)

Subscribe to and publish event objects:

```python
from hogc.lib.kernel.events import InMemoryEventBus, Event, EventPriority

# Initialize standard EventBus provider
bus = InMemoryEventBus()
bus.start()

# 1. Define event handler callback
def on_user_created(event: Event) -> None:
    print(f"Processed event: {event.event_type} for user: {event.payload.get('user_id')}")

# 2. Subscribe to routing keys (supports glob wildcard matchers)
sub_id1 = bus.subscribe("iam.user.created", on_user_created)
sub_id2 = bus.subscribe("iam.*", lambda ev: print(f"Wildcard pattern caught: {ev.event_type}"))

# 3. Publish an event
event_payload = Event(
    event_type="iam.user.created",
    tenant_id="tenant_123",
    org_id="org_456",
    source="hogc-iam-engine",
    priority=EventPriority.NORMAL,
    payload={"user_id": "usr_99"},
)
bus.publish(event_payload)

# 4. Replay events matching a pattern
history = bus.replay("iam.*")
print(f"Total replayed events: {len(history)}")

# 5. Clean up subscription
bus.unsubscribe(sub_id1)
bus.unsubscribe(sub_id2)
bus.stop()
```

---

## 5. Lifecycle Hooks (`hogc.lib.kernel.lifecycle`)

Register startup and shutdown hook actions executed during bootstrap and termination sequence:

```python
import asyncio
from hogc.lib.kernel.lifecycle import LifecycleManager, on_startup, on_shutdown

# Decorate global/module-level hooks
@on_startup(priority=10)
def init_db_connection():
    print("Database pool opened.")

@on_shutdown(priority=90)
async def flush_logs_async():
    await asyncio.sleep(0.1)
    print("Logs flushed to cloud writer.")

# Execute hooks using LifecycleManager
manager = LifecycleManager()

# Add dynamic hooks programmatically
manager.add_startup(lambda: print("Dynamic service started."), priority=20)

# Run startup hooks
manager.run_startup_hooks()

# Run shutdown hooks
manager.run_shutdown_hooks()
```

---

## 6. Policy Decorator Enforcement (`hogc.lib.contracts.policy`)

Enforce RBAC/ABAC authorization checks on service endpoints using `@enforce_policy`:

```python
from hogc.lib.contracts.policy.decorators import enforce_policy
from hogc.lib.kernel.errors import AuthorizationError

# Decorate service methods. The decorator automatically:
# 1. Resolves `PolicyService` from container (or falls back to ProviderRegistry).
# 2. Retrieves current tenant/user information from active context.
# 3. Passes the PolicyIntent to PolicyService for verification.
@enforce_policy(
    action="read", 
    resource_type="document", 
    resource_id_param="doc_id", 
    context_keys=["classification"]
)
def get_secure_document(doc_id: str, classification: str) -> dict:
    return {"id": doc_id, "content": "Sensitive Data", "level": classification}

# Usage:
# Calling get_secure_document("doc_445", "top_secret") will raise AuthorizationError
# if the active Context user roles/policies do not authorize a "read" action on the document.
```

---

## 7. Config, Secrets & Feature Flags (`hogc.lib.kernel.config`)

Interact with config/secret loaders and feature flags variants:

```python
from hogc.lib.kernel.config import ConfigProvider, SecretProvider, FeatureFlagProvider

class CoreService:
    def __init__(
        self,
        config: ConfigProvider,
        secrets: SecretProvider,
        flags: FeatureFlagProvider,
    ) -> None:
        self.config = config
        self.secrets = secrets
        self.flags = flags

    def process(self, tenant_id: str) -> None:
        # 1. Load config values
        max_limit = self.config.get_int("app.max_items_limit", default=100)

        # 2. Retrieve secure credentials
        db_password = self.secrets.get_secret("db.password")

        # 3. Check feature flags dynamically
        if self.flags.is_enabled("new-ui-v2", tenant_id=tenant_id):
            print("Running v2 path.")
        else:
            print("Running v1 fallback.")
```

---

## 8. Databases & Transactions (`hogc.lib.kernel.database`)

Establish async transactional database connections using the `UnitOfWork` pattern:

```python
from sqlalchemy import select
from hogc.lib.kernel.database import SessionFactory, UnitOfWork

# Implement a custom UnitOfWork by linking your repositories
class AccountUnitOfWork(UnitOfWork):
    def __init__(self, db: SessionFactory, schema_name: str) -> None:
        super().__init__(db, schema_name)
        # self.accounts = AccountRepository(self)
        # self.transactions = TransactionRepository(self)

# Example service implementing database queries
class BankingService:
    def __init__(self, db: SessionFactory) -> None:
        self.db = db

    async def execute_transfer(self, from_acc: str, to_acc: str, amount: float, tenant_schema: str) -> None:
        # Transactions are committed automatically if the block finishes without error
        async with AccountUnitOfWork(self.db, schema_name=tenant_schema) as uow:
            # uow.session handles the underlying active SQLAlchemy AsyncSession
            # Example update:
            # await uow.session.execute(...)
            # await uow.session.execute(...)
            await uow.commit()
```

---

## 9. Caching (`hogc.lib.kernel.cache`)

Set and get cache keys using `CacheProvider`:

```python
from hogc.lib.kernel.cache import CacheProvider

class ProductCatalog:
    def __init__(self, cache: CacheProvider) -> None:
        # Create a namespaced wrapper for clean isolation
        self.cache = cache.namespaced("catalog")

    async def get_product_details(self, product_id: str) -> dict | None:
        # 1. Try resolving from cache
        cached_data = await self.cache.get(product_id)
        if cached_data is not None:
            return cached_data  # returns dict

        # 2. Resolve from slow source (e.g. Database)
        product = {"id": product_id, "name": "Tablet", "price": 499.0}

        # 3. Save to cache with TTL
        await self.cache.set(product_id, product, ttl_seconds=3600)
        return product
```
