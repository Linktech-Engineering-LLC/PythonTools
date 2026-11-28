# PythonTools

[![License](https://img.shields.io/github/license/Linktech-Engineering-LLC/PythonTools)
![Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/PythonTools)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-active%20development-green)
![Version](https://img.shields.io/badge/version-0.2.0-blue)]

**Part of:** Linktech Engineering Tools Suite  
**Library:** PythonTools  
**Author:** Leon McClatchey, Linktech Engineering LLC  
**License:** MIT  
**Requires:** Python 3.10+  
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Design Principles](#3-design-principles)
4. [Architecture](#4-architecture)
5. [Core Capabilities](#5-core-capabilities)
6. [Modules](#6-modules)
7. [Project Ecosystem](#7-project-ecosystem)
8. [Stability Model](#8-stability-model)
9. [Roadmap](#9-roadmap)
10. [Documentation](#10-documentation)
11. [Summary](#11-summary)
12. [Notes](#12-notes)

---

## 1. Overview

PythonTools is a deterministic, reusable utility library that provides common functionality used throughout the Linktech Engineering Tools Suite.

It serves as the shared execution, networking, logging, parsing, normalization, validation, and utility layer used by multiple applications.

PythonTools is designed to provide stable capabilities while remaining independent of application-specific business logic.

---

## 2. Purpose

PythonTools exists to eliminate duplicated infrastructure code across projects.

Its goals are to:

* Provide reusable execution primitives.
* Standardize logging and error handling.
* Normalize networking and session management.
* Provide shared parsing and utility functions.
* Support deterministic behavior across applications.
* Enable cross-project consistency.

PythonTools provides capabilities.

Applications provide behavior.

---

## 3. Design Principles

PythonTools follows several core principles:

* Deterministic behavior.
* No hidden state.
* No cross-project contamination.
* Stable import surfaces.
* Reusable modular design.
* Cross-platform operation.
* Logging with redaction.
* Frozen-bundle compatibility.

PythonTools is intentionally application-agnostic.

Modules should remain reusable across multiple projects without introducing project-specific assumptions.

---

## 4. Architecture

The relationship between PythonTools and consuming applications is intentionally simple.

```text
PythonTools
    provides capabilities

Applications
    provide behavior

PythonTools
    executes

Applications
    orchestrate

Logging
    records facts

Classification
    interprets facts

Summaries
    report results
```

PythonTools does not implement application business logic.

Consuming applications remain responsible for operational behavior, workflows, and policy decisions.

---

## 5. Core Capabilities

PythonTools currently provides:

* Command execution
* SSH session management
* Networking utilities
* Structured logging helpers
* Parsing and normalization
* Schema loading and validation
* Platform and environment helpers
* Certificate utilities
* Weather data ingestion
* Monitoring integrations
* Caching services
* Date and time helpers
* Location and geospatial utilities

These capabilities are shared across multiple projects.

---

## 6. Modules

PythonTools is organized into domain-focused modules.

| Module | Purpose |
|----------|----------|
| ansible | Remote orchestration helpers |
| cache | Deterministic caching |
| certs | Certificate utilities |
| color | Terminal formatting |
| core | Shared primitives |
| datetime | Date and time utilities |
| finance | Financial normalization |
| http | HTTP client helpers |
| location | Geospatial helpers |
| log_helpers | Logging support |
| market | Market data utilities |
| nagios | Monitoring integrations |
| net | Networking helpers |
| parser | Text parsing utilities |
| parsing | Shared parsing primitives |
| sessions | Session management |
| system | Platform utilities |
| units | Unit conversions |
| utils | Transitional utilities |
| weather | Weather ingestion framework |

Modules are designed to remain isolated, reusable, and deterministic.

---

## 7. Project Ecosystem

PythonTools serves as a shared dependency for:

* RunUpdates
* NMS_Tools
* TimerDeck
* VSCode-Updater
* BotScanner
* Additional Linktech Engineering projects

This shared foundation allows projects to reuse stable implementations without duplicating common infrastructure.

---

## 8. Stability Model

PythonTools follows a conservative stability model.

Key guarantees include:

* Existing APIs remain stable.
* New modules may be added.
* Breaking changes require a version increment.
* Deterministic behavior is preserved.
* Existing consumers should not be affected by unrelated enhancements.

PythonTools is intended to be a dependable foundation layer for long-lived projects.

---

## 9. Roadmap

Current priorities include:

* Expanded module documentation.
* Automated testing.
* Semantic versioning.
* API reference generation.
* Additional provider integrations.
* Improved module coverage.
* PyPI packaging evaluation.

Roadmap priorities may evolve as ecosystem requirements change.

---

## 10. Documentation

Additional documentation is maintained within the `docs/` directory.

Planned documentation topics include:

* [Design](docs/Design.md)
* [Logging](docs/Logging.md)
* [Sessions](docs/Sessions.md)
* [Networking](docs/Networking.md)
* [Caching](docs/Caching.md)
* [Weather](docs/Weather.md)
* Nagios
* Market
* GUI
* Exception Modeling
* API Reference
* Integrations
* Troubleshooting

This README serves as the primary project overview.

---

## 11. Summary

PythonTools provides deterministic, reusable infrastructure components for the Linktech Engineering Tools Suite.

Key characteristics include:

* Reusable architecture.
* Stable behavior.
* Cross-project compatibility.
* Application independence.
* Deterministic execution.
* Long-term maintainability.

PythonTools allows consuming applications to focus on business logic rather than shared infrastructure concerns.

---

## 12. Notes

This document provides an overview of the PythonTools project.

PythonTools serves as the shared execution and utility layer for multiple Linktech Engineering projects.
