# Exhaustive Engineering Coding Standards & Architecture Guidelines

This handbook is the ultimate, non-negotiable source of truth for engineering on the HOGC platform and all Engines developed on it. It dictates exactly **how** code is written, organized, and maintained. 

The primary audience is both **Human Engineers** and **AI Coding Agents**. It is designed to remove all ambiguity, assumptions, and guesswork. If a scenario is not explicitly covered here, the core principles of explicit, type-safe, and decoupled design must guide your decision.

---

## 1. Core Engineering Principles

Every line of code must adhere to these foundational principles. They are not suggestions; they are the laws of the codebase.

### Readability over cleverness
* **What**: Code must be immediately understandable by a junior engineer. 
* **Why**: Code is read 10x more than it is written. Clever, condensed logic requires mental decompression, which causes bugs.
* **Good**: Explicit `for` loop with a clear `if` condition.
* **Bad**: A nested list comprehension spanning three lines with ternary operators.

### Explicit over implicit
* **What**: Everything a function needs must be passed to it as an argument. All return types must be declared.
* **Why**: Implicit state (like reading a global `Flask.g` variable inside a deeply nested service) hides dependencies. AI agents and humans cannot trace hidden state without reading the entire system.
* **Good**: `def process_payment(user_id: str, context: RequestContext) -> None:`
* **Bad**: `def process_payment(user_id: str) -> None:` (and reading `current_request.tenant_id` from a global object inside the function).

### Predictability over magic
* **What**: Avoid metaprogramming, runtime code generation, and complex decorators that alter function signatures or arguments dynamically.
* **Why**: When you call a function, it should do exactly what its body says. "Magic" frameworks that automatically inject variables into functions break static analyzers (Mypy) and confuse AI tools.

### Composition over inheritance
* **What**: Build complex objects by injecting simpler dependencies via the constructor, rather than inheriting from massive base classes.
* **Why**: Deep inheritance hierarchies (e.g., `class UserService(BaseCrudService, EmailNotifierService)`) lead to the "Fragile Base Class" problem. A change in the base class breaks distant subclasses unpredictably.

### Consistency over personal preference
* **What**: If the codebase uses `list[str]`, you do not use `typing.List[str]`. If the standard is early-returns, you do not use nested `if/else`.
* **Why**: A codebase must read as if it were written by one person. Uniformity minimizes cognitive friction. 

### Architecture before implementation
* **What**: Do not write a single line of logic until the interfaces (DTOs, Repository contracts, Service signatures) are defined and reviewed.
* **Why**: Plunging straight into logic leads to tight coupling. Defining the boundaries first forces you to think about separation of concerns.

### Business logic should never depend on transport protocols
* **What**: The Domain and Engine boundaries must be pure Python. They cannot import web framework modules (e.g., `fastapi`, `flask`) or parse HTTP objects.
* **Why**: In HOGC, Engines communicate via method calls on the `HOGC` facade or via the Event Bus. HTTP is a delivery mechanism handled far above the Engine layer. Engines only speak strictly typed Pydantic DTOs.

### AI should be able to predict every file location
* **What**: Standardize folder structures aggressively. If an AI creates a new service, it should know with 100% certainty that it belongs in `src/engine/services/` and ends in `_service.py`.
* **Why**: AI context windows are limited. Standardized layouts prevent the AI from having to "search" the project to figure out where things go.

### Every implementation should be replaceable
* **What**: Code against abstract interfaces/contracts, not concrete classes.
* **Why**: If you depend on `RedisCache`, swapping to `MemcachedCache` requires rewriting 50 files. If you depend on `CacheProvider`, the swap takes 1 line in the dependency injection configuration.

---

## 2. Project Architecture

The application is built in strict, concentric layers. Dependencies point **inward** (towards the domain) or **downward** (towards infrastructure). **An outer layer can call an inner layer, but an inner layer can never call an outer layer.**

### The Layers (Outer to Inner)

1. **Boundary Layers (API Gateways & Engine Providers)**
   * **Purpose**: Serve as the entry points into the system. Depending on the context, you must handle two distinct scenarios:
     1. **External API Layer (HTTP/REST)**: Translates external web requests into internal Platform calls. Handles HTTP response formatting and auth.
     2. **Internal Engine Boundary (Capabilities & Events)**: The entry point into a specific Engine. Translates Platform requests (via `@provider` or EventBus) into internal Service calls.
   * **Responsibilities**: Validate incoming Request DTOs and orchestrate internal services.
   * **Allowed to call**: Services, Contracts.
   * **Forbidden**: Repositories, Domain Entities, Databases.
   * **Rule**: No deep business logic (`if x > 5`) belongs in either boundary. They strictly delegate to internal services.

2. **Service Layer (Orchestration)**
   * **Purpose**: Execute business workflows by coordinating Repositories, external APIs, and Domain Entities.
   * **Allowed to call**: Repositories (via interfaces), Infrastructure (via interfaces), Domain, Contracts.
   * **Forbidden**: Engine Boundary Layer.
   * **Rule**: Services manage transactions (`UnitOfWork`). They fetch data, apply rules, save data, and publish events.

3. **Domain Layer (Core Logic)**
   * **Purpose**: Pure business rules and state.
   * **Allowed to call**: Nothing (except standard library and Utility layer).
   * **Forbidden**: Everything else.
   * **Rule**: The domain knows nothing about how it is saved or how it is displayed.

4. **Persistence Layer (Repositories)**
   * **Purpose**: Translate Domain/DTO objects to Database queries and vice-versa.
   * **Allowed to call**: Domain (to reconstruct entities), Contracts, Database SDK/ORM.
   * **Forbidden**: Engine Boundary, Services.
   * **Rule**: Repositories do not control transactions (no `session.commit()`). They only execute queries.

5. **Infrastructure Layer (External Systems)**
   * **Purpose**: Implement contracts for sending emails, calling external REST APIs, storing files in S3.
   * **Allowed to call**: Contracts, SDKs.
   * **Forbidden**: Engine Boundary, Services, Domain logic.

### Dependency Direction Violation Example
* **BAD**: `UserRepository` imports `NotificationService` to send a "User Created" email after inserting into the DB.
* **WHY IT IS BAD**: The Repository is a persistence mechanism. It now knows about business logic (emails). This creates a circular dependency and makes the repository impossible to test without an email server.
* **CORRECT FIX**: The `UserService` calls `UserRepository.insert(user)`, and then `UserService` calls `NotificationService.send(user)`.

---

## 3. Folder Structure Standards

Folders represent responsibilities. No ambiguity is allowed.

```text
src/my_engine/
├── providers/             # Engine Boundary (Capability Implementations & Event Handlers)
│   └── user_capability.py
├── services/              # Orchestration logic
│   └── user_service.py
├── repositories/          # DB access implementations
│   └── sql_user_repository.py
├── contracts/             # Interfaces (ABCs) and DTOs
│   ├── i_user_repository.py
│   └── user_dtos.py
├── domain/                # Pure business entities and rules
│   └── user_entity.py
├── infrastructure/        # External API clients, S3, Email
│   └── aws_s3_client.py
└── utils/                 # Pure functions ONLY (no side effects)
    └── date_parser.py
```

### Strict Folder Rules
* **No `misc`, `helpers`, `common` folders**: If you cannot name the folder by its exact responsibility, the code design is flawed. Name it `date_utils`, `string_utils`, or `math_utils`.
* **One public class per file**: If you have `CreateUserCommand` and `UpdateUserCommand`, put them in `user_commands.py`, but do not mix DTOs and Services in the same file.
* **No dumping**: Do not put random scripts in the root of `src/`. 

---

## 4. Naming Standards

Names must be literal, descriptive, and unambiguous.

### Variables & Properties
* **Rule**: Describe the value, not the type. No abbreviations.
* **Bad**: `u`, `usr`, `auth_tkn`, `max_val`, `data`, `res`.
* **Good**: `user`, `current_user`, `auth_token`, `maximum_retry_count`, `user_payload`, `capability_response`.

### Booleans
* **Rule**: Must read as a true/false statement in English.
* **Prefixes**: `is_`, `has_`, `can_`, `should_`.
* **Bad**: `active`, `validate`, `admin`, `retry`.
* **Good**: `is_active`, `has_validation_errors`, `is_admin`, `should_retry`.

### Methods & Functions
* **Rule**: Must be an action. Use `verb + noun`.
* **Bad**: `user_data()`, `process()`, `do_work()`.
* **Good**: `get_user_by_id()`, `calculate_monthly_taxes()`, `dispatch_email()`.

### Classes
* **Rule**: Must be a noun describing the responsibility.
* **Bad**: `HandlePayments`, `PerformValidation`.
* **Good**: `PaymentProcessor`, `EmailValidator`, `UserRepository`.

### Collections
* **Rule**: Must be pluralized nouns.
* **Bad**: `user_list`, `array_of_ids`, `dict_users`.
* **Good**: `users`, `user_ids`, `users_by_email`.

---

## 5. Type Safety

Static typing is mandatory. Python must be written with the strictness of TypeScript or C#.

### The "No Any" Rule
* **Rule**: The `typing.Any` type is completely forbidden across the entire codebase (not just in business logic).
* **Why**: `Any` disables Mypy. If you use `Any`, the AI cannot predict what methods exist on the object, and humans must run the code to find out. 
* **Exception**: When wrapping an untyped 3rd party library, cast the `Any` return value to a strict DTO immediately at the boundary.

### Strict Signatures
Every single function must have:
1. Typed parameters.
2. A typed return value.

* **Bad**:
  ```python
  def get_user(email=None):
      if not email: return False
      return db.query(email)
  ```
* **Good**:
  ```python
  def get_user_by_email(email: str | None) -> UserDTO | None:
      if not email:
          return None
      return self._repository.find_by_email(email)
  ```

### Nullability
* Do not rely on implicit truthiness. If a value can be null, it must be annotated as `Type | None` (or `Optional[Type]`).

### Collections
* Never write `list` or `dict` as a type.
* Always specify the contents: `list[str]`, `dict[str, UserDTO]`.

---

## 6. DTO Standards

Data Transfer Objects (DTOs) define the strict shape of data entering and leaving a boundary.

### Rules
1. **Never use `dict` for business data**: Dictionaries have no schema, no validation, and no autocomplete.
2. **Immutability**: DTOs should inherit from `PlatformModel` or `BaseDTO` (with `frozen=True`) after creation. They are data carriers, not state machines.
3. **No Behavior**: A DTO should not have methods like `dto.save_to_db()`. It is purely data.

### Standard Categories
* **RequestDTO / BaseRequest**: Data entering the system.
* **ResponseDTO / BaseResponse**: Data returning to callers.
* **Command**: Instruction to mutate state (e.g., `DeactivateAccountCommand`).

### Example (Pydantic v2)
```python
from hogc.lib.base import BaseRequest
from pydantic import Field

class CreateUserRequest(BaseRequest):
    email: str
    first_name: str = Field(..., min_length=2)
    last_name: str | None = None
```

---

## 7. Service Standards

The Service layer is the brain. It orchestrates the flow.

### Rules
1. **Stateless**: Services must not hold state in `self` across multiple requests. Dependencies (Repositories) are injected into `__init__`, but request data is passed only to methods.
2. **Orchestration only**: The service shouldn't write raw SQL. It asks the Repository for an object, applies a business rule, and asks the Repository to save it.
3. **Exception translation**: Services raise strict Platform Errors (e.g., `NotFoundError`), never HTTP exceptions.

### Example Service Method
```python
class PaymentService:
    def __init__(self, payment_repo: IPaymentRepository, user_repo: IUserRepository):
        self._payment_repo = payment_repo
        self._user_repo = user_repo

    def process_refund(self, transaction_id: str) -> RefundResultDTO:
        # 1. Fetch
        transaction = self._payment_repo.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction {transaction_id} not found.")
            
        # 2. Enforce Business Rule
        if transaction.is_already_refunded:
            raise ConflictError("Transaction already refunded.")
            
        # 3. Mutate (Domain logic)
        transaction.mark_refunded()
        
        # 4. Save
        self._payment_repo.update(transaction)
        
        return RefundResultDTO(success=True, refunded_at=transaction.refunded_at)
```

---

## 8. Repository Standards

The Repository abstracts the database. To the Service, the Repository looks like an in-memory collection of objects.

### Rules
1. **No Business Logic**: Do not check `if user.is_active` inside the repository before updating. The Service handles that check. The Repository blindly executes the update.
2. **No HTTP / Transport Awareness**: A Repository must never access request contexts directly; they are passed down via parameters.
3. **Transactions**: Repositories DO NOT call `session.commit()`. The Service orchestrating the transaction calls a `UnitOfWork.commit()` at the very end. This allows a Service to update three repositories atomically.

### Inputs & Outputs
* **Input**: Primitives (`str`, `int`), Domain Entities, or DTOs.
* **Output**: Domain Entities, DTOs, or Primitives. **Never** return an ORM model directly to the Service layer if the ORM model leaks framework methods (e.g., SQLAlchemy's lazy-loading proxy objects).

---

## 9. Boundary Standards (APIs & Engine Providers)

Boundaries must handle two distinct entry scenarios:
1. **API Layer**: An external HTTP Gateway (e.g., FastAPI/Flask) that accepts external traffic, handles auth, and calls engine capabilities.
2. **Engine Boundary**: An internal Engine provider (via `@provider` or `EventBus`) that accepts internal Platform requests.

Regardless of which boundary you are writing, the handler serves the exact same architectural purpose: validating and routing entry without holding business logic.

### The 4 Mandatory Steps of a Boundary Handler
1. **Receive**: Accept the incoming `RequestDTO` from the facade or event bus.
2. **Validate**: Ensure the request object contains valid data and context (handled natively by Pydantic).
3. **Execute**: Delegate the actual work to a specific internal Service method.
4. **Respond**: Return a `ResponseDTO` (or `BaseResponse`) back to the caller.

### Rule: No Business Logic in Boundaries
The provider class must remain paper-thin. It translates the incoming platform request into a call to internal Engine logic.

* **Bad (Logic Leakage)**:
  ```python
  @provider(RecordService, name="postgres", priority=10)
  class CRUDEngineBoundary(RecordService):
      def create_record(self, request: CreateRecordRequest) -> RecordResponse:
          # BAD: Validating permissions inside the boundary
          if "admin" not in request.context.roles:
              raise AuthorizationError("Not allowed")
              
          # BAD: Direct DB manipulation
          model = RecordModel(**request.data)
          db.session.add(model)
          db.session.flush()
          
          return RecordResponse(...)
  ```
* **Good (Thin Boundary)**:
  ```python
  @provider(RecordService, name="postgres", priority=10)
  class CRUDEngineBoundary(RecordService):
      def __init__(self, record_service: InternalRecordService):
          self._record_service = record_service

      def create_record(self, request: CreateRecordRequest) -> RecordResponse:
          # Boundary simply delegates to the core service
          return self._record_service.create_record(request)
  ```

---

## 10. Dependency Rules & Imports

Acyclic dependencies are strictly enforced.

### Rules
1. **No Circular Dependencies**: File A imports File B. File B imports File A. This causes the app to crash on startup. 
2. **No Lazy Imports**: Putting `import my_service` inside a function body (`def do_work():`) to "solve" a circular dependency is explicitly forbidden.
3. **Architectural Fix**: If A and B need each other, extract the shared logic into File C, and have both A and B import C.
4. **All Imports at Top**: Every dependency must be declared at the top of the file so humans and AI can map the dependency graph instantly.

### Import Grouping (isort standard)
1. Standard Library (`import json, os, typing`)
2. Third-Party (`from pydantic import BaseModel`, `import sqlalchemy`)
3. Internal Core Library (`from hogc.lib.kernel import PlatformContext`)
4. Internal Engine (`from my_engine.services.user_service import UserService`)

Absolute imports must be used for all internal modules. Never use relative imports (`from .user_service import...`).

---

## 11. Class Design

### Single Responsibility Principle (SRP)
* **Rule**: A class must have one reason to change. 
* **Test**: If you have to describe what a class does using the word "AND" (e.g., "It calculates taxes AND sends invoices"), it violates SRP. Split it into `TaxCalculator` and `InvoiceDispatcher`.

### Constructor Injection
* **What**: All external dependencies must be passed into the `__init__` method.
* **Why**: This allows tests to easily pass in fake/mocked repositories.
* **Forbidden**: 
  ```python
  class UserService:
      def __init__(self):
          # BAD: Hardcoded dependency. Cannot be mocked easily.
          self.repo = SQLUserRepository() 
  ```
* **Required**:
  ```python
  class UserService:
      def __init__(self, repo: IUserRepository):
          # GOOD: Injected. Testable.
          self.repo = repo
  ```

---

## 12. Method Design

Methods must be brief, focused, and predictable.

### Rules
1. **Length limit**: If a method is over 40 lines, it is doing too much. Extract private helper methods.
2. **Indentation limit**: Maximum of 3 levels of indentation (`if` inside `for` inside `if`). Deep nesting is unreadable.
3. **Guard Clauses**: Return early.
   * **BAD**: 
     ```python
     if is_valid:
         if has_permission:
             return do_work()
     ```
   * **GOOD**:
     ```python
     if not is_valid: return False
     if not has_permission: return False
     return do_work()
     ```
4. **Parameter Limit**: A method should have no more than 4 scalar arguments. If you need 5+, group them into a DTO.
5. **No Boolean Flags**: `def save(user: User, send_email: bool)` is an anti-pattern. Split into `save_user_quietly(user)` and `save_user_and_notify(user)`.

---

## 13. Comments & Documentation

Code tells you *how*. Comments tell you *why*.

### Rules
1. **Docstrings Required**: Every public class and public method must have a docstring.
2. **Format**: Use a standard format detailing Purpose, Args, Returns, and Raises.
3. **Documenting Intent**: 
   * **BAD (Useless)**: `# This adds 1 to x`
   * **GOOD (Why)**: `# We add 1 to compensate for the 0-indexed third-party API response.`

### Standard Docstring Example
```python
def process_refund(self, transaction_id: str) -> bool:
    """
    Processes a financial refund for a given transaction.

    Args:
        transaction_id: The UUID of the transaction to refund.

    Returns:
        True if the refund was successfully processed.

    Raises:
        NotFoundError: If the transaction does not exist.
        ConflictError: If the transaction was already refunded.
    """
```

---

## 14. Error Handling

Exceptions are part of the contract.

### Rules
1. **Never swallow exceptions**: 
   * **FORBIDDEN**: `try: do_x() except Exception: pass`
   * **Why**: This hides catastrophic failures (e.g., database disconnects).
2. **Never use bare excepts**: Catch the specific exception you expect (`except TimeoutError:`).
3. **Raise Platform Errors**: Raise structured platform exceptions defined in `hogc.lib.kernel.errors` (e.g., `NotFoundError`, `AuthenticationError`, `ConflictError`) rather than generic `ValueError` or `Exception`.
4. **Handle once**: If a service catches an error, either wrap it in a Domain Exception and re-raise, or resolve it. Do not log it and re-raise it, or the logs will have 5 duplicate stack traces for the same error.

---

## 15. Logging Standards

Logs are the only way to debug production. They must be structured and contextual.

### Rules
1. **Never log secrets**: Do not log passwords, API keys, authentication tokens, or personally identifiable information (PII) like full SSNs.
2. **Context is mandatory**: An error saying "Failed to update user" is useless. It must say "Failed to update user [user_id=12345, tenant_id=abc]".
3. **Use the standard Logger**: Use the platform's `LoggerContract`, never `print()`.
4. **Use `exc_info=True`**: When catching an unexpected exception, use `logger.error("Msg", exc_info=True)` to capture the stack trace.

---

## 16. Validation

Validation must be layered correctly to prevent duplication and security holes.

1. **Boundary Validation (Format/Schema)**: Happens in the Engine Boundary layer via DTOs (`BaseRequest` with Pydantic). 
   * *Example*: Is the email string formatted correctly? Is age > 0?
2. **Domain Validation (State/Rules)**: Happens in the Service/Domain layer. 
   * *Example*: Does this user's account balance exceed the purchase amount? (Requires DB lookup).
3. **Data Integrity (Persistence)**: Happens in the Database layer. 
   * *Example*: Unique constraint on `email` column to prevent race conditions.

---

## 17. Testing Standards

Tests prove that code works and lock in behavior so future refactoring doesn't break it.

### Rules
1. **Arrange, Act, Assert (AAA)**: Every test must follow this visual structure.
   ```python
   def test_refund_fails_if_already_refunded():
       # Arrange
       service = PaymentService(mock_repo)
       mock_repo.get.return_value = Transaction(is_refunded=True)
       
       # Act & Assert
       with pytest.raises(ConflictError):
           service.process_refund("123")
   ```
2. **Mock external dependencies**: In unit/service tests, mock the Repositories, email clients, and API clients.
3. **Do NOT mock data structures**: Use real DTOs and entities in your tests.
4. **Repository Tests**: Repository tests must hit a real (or in-memory) database to prove the SQL queries actually work. Mocking an ORM is useless.

---

## 18. Performance Guidelines

* **Rule 1: Measure first.** Premature optimization is the root of all evil. Write clean, O(N) readable code first. Only optimize if profiling proves it is a bottleneck.
* **Rule 2: N+1 Queries.** When fetching a list of users and their roles, do not loop over the users and query the DB for each role. Use SQL Joins (e.g., `joinedload` in SQLAlchemy).
* **Rule 3: Avoid distributed caching (Redis) unless justified.** Caching adds immense complexity regarding state invalidation. Optimize the SQL index before reaching for Redis.

---

## 19. AI-Friendly Coding Rules

To ensure AI coding agents can reliably maintain, extend, and debug this codebase, the environment must be highly deterministic.

### How AI Thinks
AI models have a limited "Context Window" (working memory). If an AI has to read 20 files to understand how a dynamic decorator works, it will fail or hallucinate. 

### Rules to Support AI
1. **Hyper-Strict Typing**: If a function returns `Any`, the AI has to guess what fields exist on the object. If it returns `UserDTO`, the AI instantly knows `.email` and `.id` are available.
2. **No Metaprogramming / Monkey Patching**: Modifying classes at runtime using `setattr()` is invisible to AI static analysis. Do not do it.
3. **Standardized Names**: If an AI is asked to "Create an Invoice feature", it will automatically attempt to generate `InvoiceBoundary`, `InvoiceService`, and `InvoiceRepository`. If you named your previous features `PaymentManager` or `BillingHandler`, the AI won't know which pattern to follow. **Be completely consistent.**
4. **Explicit Flow**: Frameworks that automatically wire things together behind the scenes via string-matching confuse AI. Constructor injection with explicit types is easily traceable by AI.

---

## 20. Python Style Restrictions

Python is extremely flexible. In this codebase, **we explicitly restrict that flexibility**. The code should read like a strongly-typed enterprise language (Java, C#, Go, TypeScript).

### Forbidden Pythonic Patterns
1. **Nested Comprehensions**: `[x for y in z for x in y if cond]` is strictly forbidden. Use standard `for` loops.
2. **Chained Ternary Operators**: `a if b else c if d else e` is strictly forbidden. Use `if/elif/else` blocks.
3. **Lambda Abuse**: Do not write complex logic inside lambdas. Define a standard `def` function.
4. **`eval()` and `exec()`**: A massive security vulnerability. Strictly forbidden.
5. **Magic Methods Abuse**: Overriding `__getattr__` or `__setattr__` hides property access. Use explicit getter/setter methods if logic is required.
6. **Inner Functions (Closures for logic)**: Defining a function inside another function (`def outer(): def inner(): ...`) is strictly forbidden unless explicitly writing a decorator. Extract them as private class methods or module-level functions so they can be unit-tested independently.

**The Goal**: An experienced C# or Go developer should be able to open any file in this repository and immediately understand the execution flow without knowing obscure Python idioms.

---

## 21. Maintainability Rules

Before committing any code, ask yourself:
1. **Is it isolated?** If I change this pricing logic, will it accidentally break user login? (If layers are respected, the answer is no).
2. **Is it replaceable?** Could a developer delete my `MailgunClient` class and write a `SendGridClient` class matching the `IEmailClient` interface without changing the Service layer?
3. **Is it discoverable?** Did I put the boundary handler in `providers/`?
4. **The Scout Rule**: Always leave the code cleaner than you found it. If you open a file to add a feature and notice missing type hints, add them.

---

## 22. Code Review Checklist

Whether reviewed by a Human or an AI Agent, a Pull Request **must not be approved** unless it passes this entire checklist:

### Architecture & Boundaries
- [ ] Code sits in the correct layer (No boundary logic in Services, no business logic in Boundaries).
- [ ] Dependencies flow strictly inward/downward.
- [ ] No transport protocols (HTTP/REST) leak into the Engine logic.
- [ ] No circular dependencies or lazy runtime imports.
- [ ] All imports are absolute and at the top of the file.

### Typing & Quality
- [ ] Mypy `strict=True` passes. No `Any` types are used in business logic.
- [ ] All method parameters and return types are strictly annotated.
- [ ] No `dict` or JSON is passed around; strict DTOs are used everywhere.
- [ ] Variables and methods have explicit, descriptive names without abbreviations.
- [ ] No complex "magic" Python tricks; the code is explicit and readable.

### Design & Testing
- [ ] Classes follow the Single Responsibility Principle.
- [ ] Constructor injection is used for all dependencies.
- [ ] Public methods have complete docstrings (Purpose, Args, Returns, Raises).
- [ ] Platform exceptions (e.g., `NotFoundError`) are raised instead of generic/built-in exceptions.
- [ ] Unit/Service tests exist and mock only external dependencies.
- [ ] Logs are structured, include context, and contain zero secrets/PII.

---
*End of Document. Consistency across the codebase is infinitely more valuable than individual coding style preferences.*
