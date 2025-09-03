## Editing guidelines for AI changes

- **Match style**: Follow Black (line length 120), isort profile black, and existing import groups.
- **Typing**: Add or preserve type hints; prefer `|` unions and standard generics (`list[str]`).
- **Error handling**: Use domain/application exceptions; in handlers, log with `exc_info` and map to `ErrorType`.
- **Logging**: Initialize a class logger via `logging.getLogger(self.__class__.__name__)`.
- **Separation**: Keep domain pure; avoid infrastructure imports in domain.
- **Transactions/side effects**: Mutate aggregates then persist via repository `.save(...)` or `.save_new_all(...)` as seen in `LLMExtractionService`.
- **Messaging**: Handlers should construct and return replies using existing builders (`CommandHandlerReplyBuilder`).
- **Do not**:
  - Introduce new wildcard imports in first-party code.
  - Reformat unrelated files.
  - Add docstrings just to satisfy linters (docstring rules are ignored by config).
- **Tests**: For new features, add unit tests under `src/tests` mirroring structure. Use pytest.
