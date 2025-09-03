## Python style for this repository

Derived from `src/pyproject.toml`, `src/setup.cfg`, and observed code.

- **Python version**: target 3.12; use typing features like `list[str] | None`, `TypedDict`, `Protocol`.
- **Formatters**: Black with line length 120; isort profile black. Do not reformat unrelated code.
- **Trailing commas**: Always use trailing commas in multi-line function calls, lists, dictionaries, imports, etc.
- **Linters**: flake8 + wemake-python-styleguide with many rule exceptions. Respect `setup.cfg` ignores and per-file-ignores.
- **Type checking**: Pyright and MyPy are enabled. Prefer explicit type annotations for public functions and complex locals. Avoid `Any` unless necessary.
- **mypy policy**: Ignore non-critical mypy/type-checking errors that don't affect runtime execution. Do not over-engineer types at the cost of clarity or delivery speed.
- **Imports** (following PEP 8):
  - Group imports in this order: 1) standard library, 2) third-party packages, 3) local/internal modules.
  - Sort alphabetically within each group.
  - Add blank lines between import groups.
  - Use absolute imports within the project package.
  - Avoid wildcard imports in first-party code.
- **Naming**:
  - Favor descriptive names over abbreviations.
  - Constants are UPPER_CASE at module scope; class-level constants are allowed as per config.
- **Functions and classes**:
  - Prefer small, focused methods with early returns; keep nesting shallow.
  - Raise domain-specific exceptions from `deps_ai_fusion.domain.exceptions` when appropriate.
  - Keep side effects clear; persist mutated aggregates via repositories.
- **Clean Architecture Flow**:
  - Endpoints -> Application Services -> Repositories/Domain Services
  - Endpoints NEVER directly use Repositories
  - Application Services orchestrate domain logic and coordinate between repositories
  - Application Services depend on Repository interfaces, not concrete implementations
- **Logging**:
  - Use `logging.getLogger(self.__class__.__name__)` in classes.
  - Log significant state transitions, saga starts/ends, and error contexts with `exc_info` as seen in `handlers.py` and services.
- **Docstrings**: NO docstrings except for very complex algorithms or public APIs that genuinely need explanation.
- **Field descriptions**: Remove obvious/redundant descriptions from Pydantic Field annotations. Only keep descriptions that provide meaningful additional context or examples.
- **API documentation**: Remove obvious summaries and descriptions from FastAPI route decorators. Let the endpoint names and response models be self-documenting.
- **Line length**: 120 characters. Wrap long expressions and function signatures across lines.
- **I/O and concurrency**: Prefer synchronous code unless existing modules are async. Follow the current sync messaging pattern.
- **Comments**: NO comments except for very complicated algorithms where you must explain WHY something complex happens. Code should be self-documenting through clear naming.
- **Empty files**: Keep `__init__.py` files empty unless they need to expose specific imports. No header comments or descriptions in empty files.
