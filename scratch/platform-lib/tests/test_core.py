import pytest

from hogc.lib.contracts.policy.decorators import enforce_policy
from hogc.lib.contracts.policy.models import PolicyDecision
from hogc.lib.contracts.policy.requests import EvaluateRequest
from hogc.lib.contracts.policy.responses import EvaluateResponse
from hogc.lib.contracts.policy.services import PolicyService
from hogc.lib.contracts.policy.types import PolicyEffect
from hogc.lib.kernel.container import Container, Scope
from hogc.lib.kernel.context import (
    ExecutionContext,
    HogcContext,
    RequestContext,
    TenantContext,
    UserContext,
    get_context_provider,
)
from hogc.lib.kernel.errors import AuthorizationError
from hogc.lib.kernel.events import Event, EventPriority, InMemoryEventBus

# ── Container Tests ─────────────────────────────────────────────────────────


def test_container_singleton():
    container = Container()

    class Dep:
        pass

    container.register(Dep, Dep)
    a = container.resolve(Dep)
    b = container.resolve(Dep)
    assert a is b


def test_container_transient():
    container = Container()

    class Dep:
        pass

    container.register(Dep, Dep, scope=Scope.TRANSIENT)
    a = container.resolve(Dep)
    b = container.resolve(Dep)
    assert a is not b


def test_container_scoped():
    container = Container()

    class Dep:
        pass

    container.register(Dep, Dep, scope=Scope.SCOPED)
    
    # Resolving scoped dependency directly from root should work and cache it
    a = container.resolve(Dep)
    b = container.resolve(Dep)
    assert a is b

    # In a child scope, it should resolve a new/isolated instance
    scope = container.create_scope()
    c = scope.resolve(Dep)
    d = scope.resolve(Dep)
    assert c is d
    assert c is not a
    scope.close()


def test_container_register_instance():
    container = Container()

    class Dep:
        pass

    instance = Dep()
    container.register_instance(Dep, instance)
    assert container.resolve(Dep) is instance


def test_container_has():
    container = Container()

    class Dep:
        pass

    assert not container.has(Dep)
    container.register(Dep, Dep)
    assert container.has(Dep)


def test_container_override():
    container = Container()

    class Dep:
        pass

    container.register(Dep, Dep)
    instance1 = container.resolve(Dep)

    mock_instance = Dep()
    with container.override(Dep, mock_instance):
        assert container.resolve(Dep) is mock_instance

    assert container.resolve(Dep) is instance1


def test_container_facade():
    from hogc.lib.kernel.container import register, register_instance, resolve

    class FacadeDep:
        pass

    register(FacadeDep, FacadeDep)
    a = resolve(FacadeDep)
    b = resolve(FacadeDep)
    assert a is b

    class FacadeInstanceDep:
        pass

    inst = FacadeInstanceDep()
    register_instance(FacadeInstanceDep, inst)
    assert resolve(FacadeInstanceDep) is inst


def test_service_facade_proxy():
    from hogc.lib.kernel.container import ServiceFacade, register

    class DummyServiceContract:
        def compute(self, val: int) -> int:
            raise NotImplementedError()

    class DummyServiceImpl(DummyServiceContract):
        def compute(self, val: int) -> int:
            return val * 10

    # Define proxy facade
    HDummyService: DummyServiceContract = ServiceFacade(DummyServiceContract)  # type: ignore[assignment]

    # Register actual implementation
    register(DummyServiceContract, DummyServiceImpl)

    # Call method via facade
    res = HDummyService.compute(5)
    assert res == 50




# ── Context Tests ───────────────────────────────────────────────────────────


def test_context_set_and_current():
    provider = get_context_provider()

    tenant = TenantContext(tenant_id="t1", org_id="o1")
    user = UserContext(user_id="u1", username="user1", email="user1@example.com", roles=["admin"])
    exec_ctx = ExecutionContext()
    req_ctx = RequestContext(tenant=tenant, user=user, execution=exec_ctx)
    platform_ctx = HogcContext(request=req_ctx)

    token = provider.set(platform_ctx)
    current_ctx = provider.current()
    assert current_ctx.request.tenant_id == "t1"
    assert current_ctx.request.user_id == "u1"
    assert "admin" in current_ctx.request.roles
    provider.reset(token)

    assert provider.current_or_none() is None


# ── Event Bus Tests ──────────────────────────────────────────────────────────


def test_in_memory_event_bus():
    bus = InMemoryEventBus()
    bus.start()

    events_received = []

    def handler(event: Event):
        events_received.append(event)

    # Test exact subscription
    bus.subscribe("iam.user.created", handler)
    # Test wildcard subscription
    bus.subscribe("iam.*", handler)

    event = Event(
        event_type="iam.user.created",
        tenant_id="t1",
        org_id="o1",
        source="iam-engine",
        priority=EventPriority.NORMAL,
        payload={"user_id": "u1"},
    )
    
    bus.publish(event)

    # Should receive 2 calls: one from iam.user.created, one from iam.*
    assert len(events_received) == 2
    assert events_received[0].payload["user_id"] == "u1"

    # Test replay
    replayed = bus.replay("iam.*")
    assert len(replayed) == 1
    assert replayed[0].event_type == "iam.user.created"

    bus.stop()


# ── Policy Decorator Tests ──────────────────────────────────────────────────


class DummyPolicyService(PolicyService):
    def __init__(self):
        self.allowed = True
        self.last_intent = None

    def evaluate(self, request: EvaluateRequest) -> EvaluateResponse:
        self.last_intent = request.intent
        decision = PolicyDecision(
            allowed=self.allowed,
            effect=PolicyEffect.ALLOW if self.allowed else PolicyEffect.DENY,
        )
        return EvaluateResponse(success=True, decision=decision)

    def create_policy(self, request): raise NotImplementedError()
    def update_policy(self, request): raise NotImplementedError()
    def delete_policy(self, request): raise NotImplementedError()
    def get_policy(self, request): raise NotImplementedError()
    def list_policies(self, request): raise NotImplementedError()
    def evaluate_batch(self, request): raise NotImplementedError()
    def grant(self, request): raise NotImplementedError()
    def revoke(self, request): raise NotImplementedError()


def test_enforce_policy_decorator():
    from hogc.lib.kernel.container import set_container

    # 1. Setup DI and Context
    container = Container()
    policy_service = DummyPolicyService()
    container.register_instance(PolicyService, policy_service)
    set_container(container)

    provider = get_context_provider()
    tenant = TenantContext(tenant_id="t1", org_id="o1")
    user = UserContext(user_id="u1", username="user1", email="user1@example.com", roles=["admin"])
    exec_ctx = ExecutionContext()
    req_ctx = RequestContext(tenant=tenant, user=user, execution=exec_ctx)
    platform_ctx = HogcContext(request=req_ctx)
    token = provider.set(platform_ctx)

    # 2. Define decorated function
    @enforce_policy(
        action="read",
        resource_type="document",
        resource_id_param="doc_id",
        context_keys=["scope"],
    )
    def get_document(doc_id: str, scope: str) -> str:
        return f"doc-{doc_id}"

    # 3. Test allowed case
    policy_service.allowed = True
    result = get_document("doc123", scope="private")
    assert result == "doc-doc123"
    assert policy_service.last_intent is not None
    assert policy_service.last_intent.action == "read"
    assert policy_service.last_intent.resource.type == "document"
    assert policy_service.last_intent.resource.id == "doc123"
    assert policy_service.last_intent.context["scope"] == "private"

    # 4. Test denied case
    policy_service.allowed = False
    with pytest.raises(AuthorizationError):
        get_document("doc123", scope="private")

    provider.reset(token)


# ── Provider Registry and Optional Fallback Tests ───────────────────────────


def test_provider_registration_optional_name():
    from hogc.lib.kernel.registry import ProviderRegistry, provider

    class TestContract:
        pass

    # Clear registry first to make sure there are no other TestContract registrations
    ProviderRegistry.clear()

    @provider(TestContract)
    class TestImpl1(TestContract):
        pass

    # Single provider registered, should be taken as default even when name is None
    cls = ProviderRegistry.get_by_name(TestContract)
    assert cls is TestImpl1

    # Add a second provider, and mark it default
    @provider(TestContract, is_default=True)
    class TestImpl2(TestContract):
        pass

    cls = ProviderRegistry.get_by_name(TestContract)
    assert cls is TestImpl2


def test_container_auto_resolve_fallback():
    from hogc.lib.kernel.container import Container
    from hogc.lib.kernel.registry import ProviderRegistry, provider

    class AutoResolveContract:
        pass

    ProviderRegistry.clear()

    @provider(AutoResolveContract)
    class AutoResolveImpl(AutoResolveContract):
        pass

    container = Container()
    # Contract is NOT registered in container, but Container should auto-resolve it
    assert not container._registrations  # confirm not manually registered
    
    resolved = container.resolve(AutoResolveContract)
    assert isinstance(resolved, AutoResolveImpl)
    
    # Confirm it got cached as a singleton registration on-the-fly
    assert container.has(AutoResolveContract)
    assert container.resolve(AutoResolveContract) is resolved


def test_enforce_policy_decorator_fallback():
    from hogc.lib.kernel.container import set_container
    from hogc.lib.kernel.registry import ProviderRegistry, provider

    ProviderRegistry.clear()

    # 1. Setup DI using dummy/empty container to force resolution failure in first step
    container = Container()
    set_container(container)

    # 2. Register dummy policy service in ProviderRegistry
    @provider(PolicyService, default=True)
    class FallbackPolicyService(DummyPolicyService):
        pass

    provider_ctx = get_context_provider()
    tenant = TenantContext(tenant_id="t1", org_id="o1")
    user = UserContext(user_id="u1", username="user1", email="user1@example.com", roles=["admin"])
    exec_ctx = ExecutionContext()
    req_ctx = RequestContext(tenant=tenant, user=user, execution=exec_ctx)
    platform_ctx = HogcContext(request=req_ctx)
    token = provider_ctx.set(platform_ctx)

    @enforce_policy(action="read", resource_type="document")
    def my_secured_function() -> str:
        return "success"

    try:
        # Calls the function; should auto-resolve PolicyService via provider registry fallback
        res = my_secured_function()
        assert res == "success"
    finally:
        provider_ctx.reset(token)


def test_hogc_facade():
    from hogc.lib import HOGC
    from hogc.lib.contracts.policy.services import PolicyService
    from hogc.lib.kernel.container import Container, resolve, set_container
    from hogc.lib.kernel.registry import ProviderRegistry, provider

    ProviderRegistry.clear()

    # 1. Setup DI container
    container = Container()
    set_container(container)

    @provider(PolicyService)
    class TestPolicyService(DummyPolicyService):
        pass

    # 2. Test accessing a service directly as a property (snake_case)
    assert hasattr(HOGC, "policy")
    
    # Get active resolved service
    instance = resolve(PolicyService)
    
    # 3. Verify it resolves to our registered instance
    assert HOGC.policy is instance
    assert hasattr(HOGC.policy, "evaluate")


