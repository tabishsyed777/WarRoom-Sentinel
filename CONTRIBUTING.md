# Contributing to WarRoom Sentinel

Thank you for contributing.

## Safety requirements

- Keep all behavior fictional, local, and simulation-only.
- Do not add exploit code, scanning, real-network connections, or credential handling.
- Model new behavior as validated game-state actions and probability rules.

## Development

```bash
python3 -m unittest discover -s tests -v
```

When changing a rule, add or update a deterministic test for it.
