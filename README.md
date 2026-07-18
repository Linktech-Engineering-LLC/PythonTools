# PythonTools

![Status: Under Construction](https://img.shields.io/badge/status-under_construction-yellow.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)

PythonTools is a deterministic, cross‑project utility library providing stable primitives for execution, logging, path resolution, schema loading, and exception modeling. It is the foundational support library used across the **Linktech Engineering Tools Suite**, including RunUpdates, VSCode‑Updater, NMS_Tools, TimerDeck, BotScanner and other operator‑grade automation projects.

PythonTools is designed so that adding new functionality **cannot negatively affect other projects** importing it. Modules are isolated, deterministic, and safe for reuse across multiple applications.
---

## Related Project: RunUpdates

![RunUpdates Status](https://img.shields.io/badge/RunUpdates-Active-green.svg)
![RunUpdates License](https://img.shields.io/badge/license-MIT-blue.svg)
![RunUpdates Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)
[![RunUpdates Dashboard](https://img.shields.io/badge/RunUpdates-Dashboard-blue)](https://linktech-engineering-llc.github.io/RunUpdates/)
[![RunUpdates Stable](https://img.shields.io/badge/RunUpdates-Stable-green)](https://linktech-engineering-llc.github.io/RunUpdates/stable/)

PythonTools provides foundational components used by  
**RunUpdates** → https://github.com/Linktech-Engineering-LLC/RunUpdates

## Related Project: NMS_Tools

![NMS_Tools](https://img.shields.io/badge/NMS_Tools-Uses_PythonTools-blueviolet.svg)
![NMS_Tools Status](https://img.shields.io/badge/NMS_Tools-Active-green.svg)
![NMS_Tools License](https://img.shields.io/badge/license-MIT-blue.svg)
![NMS_Tools Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)
[![NMS_Tools Dashboard](https://img.shields.io/badge/NMS_Tools-Dashboard-green)](https://linktech-engineering-llc.github.io/NMS_Tools/)
[![NMS_Tools Stable](https://img.shields.io/badge/NMS_Tools-Stable-green)](https://linktech-engineering-llc.github.io/NMS_Tools/stable/)

PythonTools provides foundational components used by  
**NMS_Tools** → https://github.com/Linktech-Engineering-LLC/NMS_Tools

NMS_Tools relies on PythonTools for:

- deterministic subprocess execution  
- unified logging and redaction  
- schema loading and validation  
- market/finance provider architecture  
- ticker normalization and trend analysis  
- weather and network data ingestion  
- frozen‑bundle compatibility for distribution  

---

## Overview

PythonTools provides stable, reusable modules intended for use across multiple operator‑grade projects. These modules implement deterministic patterns for:

* subprocess execution
* path and environment resolution
* structured JSON logging
* exception modeling
* schema loading and validation
* normalization and inheritance helpers
* frozen‑bundle compatibility

The goal is to centralize shared logic so application‑level projects remain clean, predictable, and focused.

PythonTools is not a “common utilities dumping ground.”
It is a *stable foundation layer** for the entire Linktech Engineering ecosystem.

---

## Design Guarantees

PythonTools follows strict design rules:

* **Deterministic behavior** — no nondeterministic helpers or hidden state
* **No global state mutation** — modules never modify shared global variables
* **No cross‑project contamination** — importing PythonTools cannot break other projects
* **Stable import surface** — modules expand, but existing behavior remains stable
* **Predictable subprocess wrappers** — normalized exit codes, stdout/stderr, and error modeling
* **Consistent exception types** — unified error model across all projects
* **Safe logging with redaction** — secrets never logged
* **Frozen‑bundle compatibility** — works inside PyInstaller, zipapp, and frozen distributions

These guarantees allow PythonTools to serve as a reliable backbone for multiple automation systems.

---

## Modules 

PythonTools is organized into domain‑specific modules. Each module is isolated, deterministic, and safe for cross‑project import.

| Module | Purpose |
| --- | --- |
| **ansible** | Automation helpers for remote orchestration and playbook execution. Provides deterministic wrappers for Ansible‑based tasks and configuration management. |
| **core** | Foundational primitives — constants, base classes, and shared logic used by other modules. Defines the stable backbone of PythonTools. |
| **finance** | Utilities for financial or transactional data processing, normalization, and reporting. |
| **log_helpers** | Structured logging, redaction, and formatting utilities. (To be merged into the unified ``logging`` module.) |
| **market** | Market and analytics helpers for data exchange, pricing, or trading integrations. |
| **nagios** | Monitoring and alerting integration layer for Nagios and compatible systems. |
| **net** | Networking helpers — sockets, SSH, HTTP, and connection utilities. |
| **parser** | Text and stdout parsing utilities used by RunUpdates and other projects for universal output classification. |
| **sessions** | Connection/session management for SSH, API, or local subprocess sessions. |
| **utils** | Generic helpers and transitional functions. These will be migrated into domain‑specific modules as stabilization continues. |

Each module follows the same design guarantees:

* deterministic behavior
* no global state mutation
* safe cross‑project import
* consistent exception and logging models

---

## 🧩 Project Ecosystem

PythonTools is the shared foundation for the Linktech Engineering Tools Suite:

* **RunUpdates** — update orchestration and system maintenance
* **NMS_Tools** — network management, market data, weather ingestion, and system checks
* **TimerDeck** — systemd automation and scheduling
* **VSCode-Updater** — editor update automation
* **BotScanner** — security analysis and behavioral scanning

This ecosystem relies on PythonTools for deterministic execution, logging, schema validation, and cross‑project stability.

---

### 🧩 Module Relationships Diagram

PythonTools modules form a layered architecture.
Lower‑level modules provide primitives; higher‑level modules compose them into domain‑specific functionality.

```Code
                         +----------------------+
                         |      ansible         |
                         |  (automation layer)  |
                         +----------+-----------+
                                    |
                                    v
+------------------+     +----------------------+     +------------------+
|      market      | <-- |       finance        | --> |      nagios      |
| (analytics/data) |     | (transaction logic)  |     | (monitoring)     |
+------------------+     +----------------------+     +------------------+
            \                     |                         /
             \                    |                        /
              \                   v                       /
               \        +----------------------+         /
                \------ |       parser         | -------/
                        | (stdout/text parse)  |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |       sessions       |
                        | (SSH/API/local exec) |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |         net          |
                        | (network helpers)    |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |         exec         |
                        | (subprocess engine)  |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |         core         |
                        | (constants/base)     |
                        +----------+-----------+
                                   |
                                   v
                        +----------------------+
                        |        utils         |
                        | (transitional code)  |
                        +----------------------+
```

### 🔍 Relationship Summary
* **core**
    The foundation. Everything ultimately depends on it.

* **exec**
    Built on core. Provides deterministic subprocess execution used by sessions, net, and indirectly by higher modules.

* **net**
    Networking primitives built on exec.

* **sessions**
    Connection/session management built on net + exec.

* **parser**
    Consumes sessions output and provides normalized parsing utilities.

* **finance, market, nagios**
    Domain‑specific modules that depend on parser, sessions, and sometimes net.

* **ansible**
    High‑level automation layer built on sessions, net, and exec.

* **utils**
    Transitional helpers — gradually being migrated into domain‑specific modules.

---

## Used By

PythonTools is the foundational library used across:

* **RunUpdates** — update orchestration and system maintenance  
* **NMS_Tools** — network management suite (tickers, weather, system checks, market providers)  
* **TimerDeck** — systemd automation and scheduling  
* **BotScanner** — security tooling and behavioral analysis  
* **VSCode-Updater** — editor update automation  
* Additional internal Linktech Engineering tools

---

## Project Status

PythonTools is in active development.
Modules are being stabilized as they are exported from existing projects.

The public API surface is becoming stable, and breaking changes will follow semantic versioning rules.

---

## Roadmap

* Document subprocess wrappers
* Document path/env resolution
* Document logging model
* Document exception model
* Add semantic versioning
* Add automated tests
* Prepare for PyPI packaging
* Add module reference pages

---

## Stability Model

PythonTools follows a stability model:

* Existing APIs remain stable
* New modules may be added
* Breaking changes require a version bump
* Behavior is deterministic across all supported environments

---

## Philosophy

PythonTools exists to keep application‑level projects clean, deterministic, and focused.
It provides stable primitives so projects never need to reinvent execution, logging, or path resolution.

## License

MIT License
