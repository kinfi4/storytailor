## Testing practices (single source of truth)

Use this as the reference for how tests are written in this repo. Follow these rules when creating or editing tests.

- **framework**: pytest with pytest-mock, pytest-factoryboy, Starlette `TestClient`.
- **layout**: tests live under `src/tests` with clear separation:
  - `src/tests/unit/...` for pure unit tests (domain, application, handlers)
  - `src/tests/integration/...` for integration tests (FastAPI endpoints, repositories)
  - shared helpers in `src/tests/factories`, `src/tests/fakes`, `src/tests/data`
- **naming**: files as `test_*.py`; functions as `test_*`; group by feature or endpoint (classes optional, e.g., `TestAnalysis`).

### Fixtures and DI

- **global fixtures** are defined in `src/tests/conftest.py`, `src/tests/unit/conftest.py`, `src/tests/integration/conftest.py`, and subpackage `conftest.py` files.
- **FastAPI app**: session-scoped fixture `app` uses `create_fastapi()`; the `client` fixture yields a `TestClient(app)`.
- **DI containers**: access via `containers` fixture (`app.containers`). When overriding:
  - Use container override context managers and reset singletons:
    - `with containers.providers_aggregate.override(FakeProvidersAggregate()): ...`
    - `containers.reset_singletons()` or `repositories.reset_singletons()` where appropriate
  - Example pattern for mocking a proxy/service:
    ```python
    with containers.proxies.extraction.override(mocker.Mock(containers.proxies.extraction.cls)):
        yield containers.proxies.extraction()
    ```
- **fakes**: prefer concrete fakes over generic mocks when available:
  - `tests/fakes/FakeLLMExtractorRepository`, `FakeProvidersAggregate`, `FakeFileStorage`
  - Override container providers with fakes in fixtures
- **factories**: use pytest-factoryboy registration (see `register(...)` in `integration/conftest.py`): fixtures like `llm_extractor_factory`, `ConversationFactory`, etc., produce domain objects.

### API tests

- Use `authenticated_client` fixture that sets the `deps-token` header from `tests.factories.test_user_data`.
- Endpoints are prefixed with `V1_API_PREFIX`; build URLs with it.
- Always assert status codes first, then parse JSON via `response.json()`.
- Validate response structure using camelCase keys. When comparing to Pydantic models, use `.model_dump(mode="json", by_alias=True)`.
- Build request payloads via builder fixtures (e.g., `raw_query_with_single_node_request_factory`) to keep tests focused on behavior.
- For provider-driven flows:
  - Arrange: `fake_providers_aggregate.set_response("some_value")`
  - Act: call the endpoint or application service
  - Assert: use `fake_providers_aggregate.assert_insights_retrival_request_made_with(provider=..., model=...)` when applicable

### Application and domain tests

- Save aggregates into fake repositories before invoking services that read them:
  ```python
  fake_llm_extractor_repository.save(llm_extractor)
  ```
- Use domain methods and value objects directly; verify side effects by reading back from the fake repository and asserting changes.
- For workflows and queries, use fixtures like `test_raw_llm_workflow`, `test_llm_workflow`, `test_raw_data_shape`, `test_code`.
- Use `uuid4().hex` for identifiers in tests and fixtures.
- Keep assertions explicit and close to behavior: number of queries, prompt updates, etc.

### Handlers and messaging

- Handlers are thin; test them with mocks/fakes of application services:
  - Use `mock_extraction_service` fixture (DI override with `mocker.Mock`) and verify replies
  - Use `pytest.raises` for error branches in application layer; in handlers assert the reply payload contains `error_type`/`error_message` as expected

### Mocking vs fakes

- Prefer fakes from `tests/fakes` for repositories and providers.
- Use `mocker` for lightweight behavior verification (e.g., `mock_extraction.save_extracted_data.assert_called()` / `.assert_not_called()`).
- Avoid global monkeypatching; interact via DI overrides.

### Parametrization and patterns

- Use `@pytest.mark.parametrize` to cover input combinations (e.g., provider@model parsing, invalid request shapes).
- Follow Arrange–Act–Assert. Keep each test focused and readable.
- No unnecessary docstrings in tests; inline comments only for non-obvious intent.
- You may skip non critical mypy, linter errors.

### Data and randomness

- Randomness is used in fixtures to vary structures (`random.choice`, random lengths). Do not assert on random values; assert on structural properties or values derived from the action.

### Serialization and aliases

- Requests/responses use camelCase. Serializers should use Pydantic v2 with `by_alias=True` in dumps and accept alias fields on input.
- In tests, build JSON using camelCase keys; when asserting against models, prefer `.model_dump(mode="json", by_alias=True)`.

### Repository and side-effects

- Verify persistence by loading from the repository after the call (`find_for_document_type`, `find_by_id`) and asserting the aggregate state.
- Ensure deletion/update flows reduce or change repository contents accordingly.

### Structure for new tests

- Place unit tests close to the feature under `src/tests/unit/<area>/test_*.py`.
- Place API/integration tests under `src/tests/integration/...` or `src/tests/unit/api/...` depending on scope.
- Prefer function-level tests; group in classes when it improves readability for endpoints.
- For function-level tests make sure to have two blank lines between test functions.

### Antipatterns to avoid

- Do not hit real external services or files; use fakes and DI overrides.
- Do not rely on vendor implementations; treat `vendors/` as external.
- Do not assert internal implementation details of DI; assert observable behavior and side effects.

### Running tests locally

- Unit tests: `make tests-unit`
- Integration tests: `make tests-integration`
- All + coverage: `make tests && make coverage`
