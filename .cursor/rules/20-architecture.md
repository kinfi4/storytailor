## Architecture and boundaries

This project uses layered, DDD-influenced architecture with messaging and sagas.

- **Layers**:
  - `domain`: Entities, value objects, aggregates, repositories' interfaces, domain events/exceptions. No external I/O.
  - `application`: Orchestrates use cases, coordinates repositories, sagas, messaging, and services (`LLMExtractionService`).
  - `infrastructure`: Implementations of repositories/services, provider orchestration (`LLMsController`), proxies.

- **Rules**:
  - Domain must not depend on application/infrastructure.
  - Application may depend on domain and interfaces; call infrastructure via DI containers.
  - Messaging handlers must be thin and delegate to application services.
  - Persist aggregates only through repositories; do not leak ORM/DB details into domain.
  - Use `ProviderCode` and provider/model lookups via `ProvidersAggregate` through `LLMsController`.

- **Error handling**:
  - Raise `BusinessError` subclasses for domain/application errors.
  - In handlers, map exceptions to `ErrorType` and reply with structured messages.
