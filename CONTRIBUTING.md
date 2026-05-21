# Contributing to PythonTools

Thank you for your interest in contributing to **PythonTools**.  
This library provides shared modules, constants, and tooling primitives used across multiple Linktech Engineering projects.  
Contributions that improve clarity, correctness, maintainability, and reusability are welcome.

---

## Development Philosophy

PythonTools is designed to be:

- **Lightweight** — minimal dependencies, no heavy frameworks  
- **Reusable** — modules must be generic and project‑agnostic  
- **Predictable** — deterministic behavior, explicit logic, no hidden side effects  
- **Stable** — public APIs should remain consistent once finalized  
- **Documented** — modules should be self‑describing and easy to adopt  

If a feature belongs to a specific application (e.g., RunUpdates), it should remain in that project.

---

## How to Contribute

### 1. Fork the repository

```bash
git clone https://github.com/Linktech-Engineering-LLC/PythonTools.git
cd PythonTools
```

### 2. Create a feature branch

```git checkout -b feature/my-improvement```

### 3. Make your changes
Please ensure:

* Code is clean, explicit, and readable
* No project‑specific logic is introduced
* Public APIs are documented
* Constants are well‑named and typed
* Modules remain import‑safe and dependency‑light
* Behavior is deterministic and testable

### 4. Add or update tests (when applicable)

Tests should be:

* Minimal
* Focused
* Deterministic
* Free of external dependencies

### 5. Submit a pull request

Your PR should include:

* A clear description of the change
* Why it improves the library
* Any relevant examples or test updates
* Confirmation that it does not break existing imports

## Project Structure

PythonTools/
  ansible/        # Schema loaders, validators, normalization logic
  utils/          # Shared utility modules
  constants/      # Common constants (future)
  ...

New modules should fit cleanly into this structure or propose a logical extension.

## Code Style

* Follow standard Python conventions (PEP 8)
* Prefer explicit over implicit
* Avoid unnecessary abstraction
* Keep functions small and focused
* Use type hints consistently
* Avoid side effects in module import paths

## Reporting Issues

If you encounter a bug or have a feature request:

* Open an issue
* Provide a clear description
* Include reproduction steps if applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

