## Prompting conventions for this workspace

- **Default response style**: concise bullets and short code blocks. Avoid long narration.
- **When proposing code**: Provide edits, not full files. Include only changed regions. Keep imports accurate.
- **When running commands**: Use absolute paths (e.g., `/home/kinfi4/WORK/deps-root/deps-ai-fusion`). Pass non-interactive flags and pipe pagers to `| cat` when necessary.
- **Assumptions**: If a required detail (env var, secret, model code) is missing, state a safe default and proceed, marking a TODO for the value.
- **Vendor code**: Treat under `vendors/` as external. Do not refactor or reformat; only interact through published interfaces.
