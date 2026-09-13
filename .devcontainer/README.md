# JARVIS Enterprise — Codespace

The repository defines its development environment through `.devcontainer/devcontainer.json`.

## Workflow

1. Open or create a GitHub Codespace from the repository.
2. The container installs the JARVIS package in editable mode.
3. Hermes is prepared through `scripts/setup_hermes.sh` when the setup is available.
4. Develop on a dedicated branch; keep `main` as the stable integration branch.
5. Run the local validation before committing:

```bash
python -m unittest discover -s tests -v
```

6. Push the branch and open a pull request.
7. GitHub Actions validates the package and test suite.
8. Merge only after the validation is successful.

Model-backed Hermes execution remains dependent on the isolated Hermes runtime and provider credentials; credentials must never be committed to Git.
