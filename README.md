# PythonTools

**Part of:** Linktech Engineering Tools Suite  
**Library:** PythonTools  
**Author:** Leon McClatchey, Linktech Engineering LLC  
**License:** MIT  
**Requires:** Python 3.10+  
**Last Updated:** 2026‑08‑20

![Status: Under Construction](https://img.shields.io/badge/status-under_construction-yellow.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)
![Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/PythonTools)

PythonTools is a deterministic, cross‑project utility library providing stable primitives for execution, logging, path resolution, schema loading, and exception modeling. It is the foundational support library used across the **Linktech Engineering Tools Suite**, including RunUpdates, VSCode‑Updater, NMS_Tools, TimerDeck, BotScanner and other operator‑grade automation projects.

PythonTools is designed so that adding new functionality **cannot negatively affect other projects** importing it. Modules are isolated, deterministic, and safe for reuse across multiple applications.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Design Guarantees](#2-design-guarantees)
3. [Modules](#3-modules)
4. [Weather Provider Architecture](#4-weather-provider-architecture)
5. [Project Ecosystem](#-5-project-ecosystem)
6. [Module Relationships Diagram](#6-module-relationships-diagram)
7. [Used By](#7-used-by)
8. [Related Project: RunUpdates](#8-related-project-runupdates)
9. [Related Project: NMS_Tools](#9-related-project-nms_tools)
10. [Project Status](#10-project-status)
11. [Roadmap](#11-roadmap)
12. [Stability Model](#12-stability-model)
13. [Philosophy](#13-philosophy)
14. [License](#14-license)

---

## 1. Overview

PythonTools provides stable, reusable modules intended for use across multiple operator‑grade projects. These modules implement deterministic patterns for:

* subprocess execution
* path and environment resolution
* structured JSON logging
* exception modeling
* schema loading and validation
* normalization and inheritance helpers
* frozen‑bundle compatibility

PythonTools is not a “common utilities dumping ground.”
It is a *stable foundation layer** for the entire Linktech Engineering ecosystem.

---

## 2. Design Guarantees

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

## 3. Modules

PythonTools is organized into domain‑specific modules. Each module is isolated, deterministic, and safe for cross‑project import.

| Module      | Purpose |
|------------|---------|
| **ansible** | Automation helpers for remote orchestration and playbook execution. |
| **cache**   | Deterministic caching helpers for provider and subsystem data. |
| **certs**   | Certificate and trust store helpers for secure connections. |
| **color**   | Color and style helpers for terminal or structured output. |
| **core**    | Foundational primitives — constants, base classes, shared logic. |
| **datetime**| Date/time helpers, normalization, and deterministic time handling. |
| **finance** | Financial/transactional normalization and reporting. |
| **http**    | HTTP client helpers and request/response normalization. |
| **location**| Location and coordinate helpers (lat/lon, geospatial context). |
| **log_helpers** | Structured logging, redaction, formatting utilities. |
| **market**  | Market analytics, pricing, and trading integrations. |
| **nagios**  | Monitoring and alerting integration for Nagios systems. |
| **net**     | Networking helpers — sockets, SSH, HTTP, connection utilities. |
| **parser**  | Text/stdout parsing utilities used by RunUpdates and others. |
| **parsing** | Shared parsing primitives and normalization helpers. |
| **sessions**| SSH/API/local subprocess session management. |
| **system**  | System‑level helpers (environment, platform, process context). |
| **units**   | Unit conversion and normalization helpers. |
| **utils**   | Transitional helpers; gradually migrated into domain modules. |
| **weather** | Weather provider architecture and normalized ingestion engine. |

Each module follows the same design guarantees:

* deterministic behavior
* no global state mutation
* safe cross‑project import
* consistent exception and logging models

---

## 4. Weather Provider Architecture

PythonTools includes a deterministic, provider‑agnostic weather ingestion subsystem used by NMS_Tools and other Linktech Engineering projects. The subsystem provides unified access to multiple upstream weather providers through a stable, normalized schema.

### Provider Registry

Weather providers register themselves through the `WEATHER_PROVIDERS` dictionary.  

```python
WEATHER_PROVIDERS["nws"].update({
"supports": ("current", "hourly", "weekly", "full"),
"fetch_current": fetch_current_nws,
"fetch_hourly": fetch_hourly_nws,
"fetch_weekly": fetch_weekly_nws,
"fetch_full": fetch_full_nws,
})
```

Each provider implements:

```python
fetch_current(lat, lon, timeout, meta)
fetch_hourly(lat, lon, timeout, meta)
fetch_weekly(lat, lon, timeout, meta)
fetch_full(lat, lon, timeout, meta)
```

### Unified Modes

PythonTools normalizes all provider output into a deterministic schema:

```python
{
"current": {...},
"hourly": {...},
"weekly": {...},
"alerts": {...}
}
```

Mode definitions:

* **current** — single observation block  
* **hourly** — 24–48 hour forecast  
* **weekly** — 7–10 day forecast  
* **full** — composite mode: current + hourly + weekly  

Alerts are appended by the caller (e.g., NMS_Tools `check_weather`).

### Meta Model

The `meta` object carries deterministic provider metadata:

* `cached_obs` — NWS observation used for feels‑like, dewpoint, pressure  
* `cached_station_id` — NWS station identifier  
* provider URLs (when available)  
* provider‑specific metadata

NWS observations are fetched automatically for:

* NWS: hourly, weekly, full  
* Open‑Meteo: weekly, full  

This ensures consistent feels‑like and dewpoint values across providers.

### Unified Index Model

All providers normalize environmental indices:

```python
index: {
heat_index,
wind_chill,
humidex,
wet_bulb,
vapor_pressure,
saturation_vapor_pressure,
mixing_ratio,
specific_humidity,
air_density,
pressure_altitude
}
```

PythonTools guarantees deterministic calculations and fallback logic.

### Condition Code Normalization

Providers return different condition codes.  
PythonTools normalizes them into a unified set:

* `condition` — numeric code  
* `context` — human‑readable description  
* `icon` — deterministic icon name

### Deterministic Output Schema

PythonTools guarantees:

* identical schema across providers  
* identical schema across modes  
* identical schema across locations  
* identical schema across frozen and non‑frozen builds

---

## 🧩 5. Project Ecosystem

PythonTools is the shared foundation for the Linktech Engineering Tools Suite:

* **RunUpdates** — update orchestration and system maintenance
* **NMS_Tools** — network management, market data, weather ingestion, and system checks
* **TimerDeck** — systemd automation and scheduling
* **VSCode-Updater** — editor update automation
* **BotScanner** — security analysis and behavioral scanning

This ecosystem relies on PythonTools for deterministic execution, logging, schema validation, and cross‑project stability.

---

## 6. Module Relationships Diagram

\`\`\`
   ┌──────────────────────────┐
   │        DATA CORE         │
   │ core, units, system,     │
   │ datetime, location, cache│
   └───────────┬──────────────┘
               │
               ▼
   ┌──────────────────────────┐
   │      PARSING CORE        │
   │ parser, parsing,         │
   │ log_helpers              │
   └───────────┬──────────────┘
               │
               ▼
   ┌──────────────────────────┐
   │      NETWORK CORE        │
   │ net, http, sessions      │
   └───────────┬──────────────┘
               │
               ▼
   ┌──────────────────────────┐
   │      DOMAIN LAYERS       │
   └──────────────────────────┘

   market ↔ finance

   weather → nagios
   parsing → nagios
   location → nagios
   net → nagios
   http → nagios

   ansible → RunUpdates
   RunUpdates → parsing, net, sessions, system, core

   parser → market, finance, nagios, RunUpdates
\`\`\`


---

## 7. Used By

PythonTools is used across:
* RunUpdates
* NMS_Tools
* TimerDeck
* BotScanner
* Additional internal tools

---
## 8. Related Project: RunUpdates

![RunUpdates Status](https://img.shields.io/badge/RunUpdates-Active-green.svg)
![RunUpdates License](https://img.shields.io/badge/license-MIT-blue.svg)
![RunUpdates Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)
[![RunUpdates Dashboard](https://img.shields.io/badge/RunUpdates-Dashboard-blue)](https://linktech-engineering-llc.github.io/RunUpdates/)
[![RunUpdates Stable](https://img.shields.io/badge/RunUpdates-Stable-green)](https://linktech-engineering-llc.github.io/RunUpdates/stable/)
![RunUpdates Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/RunUpdates)

PythonTools provides foundational components used by  
[**RunUpdates**](https://github.com/Linktech-Engineering-LLC/RunUpdates)

RunUpdates relies on PythonTools for:
* deterministic subprocess execution
* session and connection management
* stdout parsing and normalization
* system/environment resolution
* logging and redaction
* frozen‑bundle compatibility

---

## 9. Related Project: NMS_Tools

![NMS_Tools](https://img.shields.io/badge/NMS_Tools-Uses_PythonTools-blueviolet.svg)
![NMS_Tools Status](https://img.shields.io/badge/NMS_Tools-Active-green.svg)
![NMS_Tools License](https://img.shields.io/badge/license-MIT-blue.svg)
![NMS_Tools Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Linktech Engineering Tools Suite](https://img.shields.io/badge/Linktech_Engineering-Tools_Suite-blueviolet.svg)
[![NMS_Tools Dashboard](https://img.shields.io/badge/NMS_Tools-Dashboard-green)](https://linktech-engineering-llc.github.io/NMS_Tools/)
[![NMS_Tools Stable](https://img.shields.io/badge/NMS_Tools-Stable-green)](https://linktech-engineering-llc.github.io/NMS_Tools/stable/)
![NMS_Tools Last Commit](https://img.shields.io/github/last-commit/Linktech-Engineering-LLC/NMS_Tools)

PythonTools provides foundational components used by  
[**NMS_Tools**](https://github.com/Linktech-Engineering-LLC/NMS_Tools)

NMS_Tools relies on PythonTools for:
* deterministic subprocess execution
* unified logging and redaction
* schema loading and validation
* market/finance provider architecture
* ticker normalization and trend analysis
* weather and network data ingestion
* stdout parsing and normalization
* frozen‑bundle compatibility for distribution

---

## 10. Project Status

PythonTools is in active development.
Modules are being stabilized as they are exported from existing projects.

---

## 11. Roadmap

* Document subprocess wrappers
* Document path/env resolution
* Document logging model
* Document exception model
* Add semantic versioning
* Add automated tests
* Prepare for PyPI packaging
* Add module reference pages

---

## 12. Stability Model

PythonTools follows a stability model:

* Existing APIs remain stable
* New modules may be added
* Breaking changes require a version bump
* Behavior is deterministic across all supported environments

---

## 13. Philosophy

PythonTools exists to keep application‑level projects clean, deterministic, and focused.
It provides stable primitives so projects never need to reinvent execution, logging, or path resolution.

---

## 14. License

MIT License

---

