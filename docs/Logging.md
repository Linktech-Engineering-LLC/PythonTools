# PythonTools Logging

**Part of:** Linktech Engineering Tools Suite
**Document:** Logging
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** PythonTools
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Logging Philosophy](#3-logging-philosophy)
4. [Logger Injection](#4-logger-injection)
5. [NullLogger](#5-nulllogger)
6. [Structured Logging](#6-structured-logging)
7. [Redaction](#7-redaction)
8. [Responsibility Boundaries](#8-responsibility-boundaries)
9. [Stability Model](#9-stability-model)
10. [Summary](#10-summary)
11. [Notes](#11-notes)

---

## 1. Overview

PythonTools provides logging infrastructure for consuming applications.

The library does not define logging policy, destination, retention, formatting, or operational requirements.

Instead, PythonTools receives a logger from the consuming application and uses that logger throughout execution.

This approach allows multiple applications to share a common logging model while maintaining independent logging policies.

---

## 2. Purpose

The PythonTools logging subsystem exists to:

* Provide a consistent logging interface.
* Support deterministic execution tracing.
* Enable structured logging.
* Prevent secret leakage.
* Eliminate duplicate logging implementations.
* Support application-defined logging policies.

PythonTools records facts.

Applications decide what those facts mean.

---

## 3. Logging Philosophy

PythonTools follows several logging principles.

### Deterministic

Logging should accurately represent execution events.

The same operation should produce the same logging behavior regardless of the consuming application.

### Application-Controlled

Applications own:

* Log destinations.
* Log rotation.
* Log retention.
* Log formatting.
* Log storage policy.

PythonTools consumes the logger but does not manage it.

### Safe

Sensitive information must never be written to logs.

Secrets should be redacted before being logged.

### Structured

Logging should provide meaningful execution context rather than unstructured console output.

---

## 4. Logger Injection

PythonTools does not initialize logging.

Instead, applications inject a logger instance.

Example:

```python
from PythonTools.logging import set_logger

set_logger(application_logger)
```

After injection, PythonTools uses the supplied logger for all logging operations.

This allows applications to maintain complete control over logging behavior.

---

## 5. NullLogger

PythonTools provides a NullLogger implementation.

If no logger is supplied:

* Logging calls remain valid.
* No output is generated.
* No exceptions are raised.
* Execution continues normally.

This allows PythonTools to operate safely in:

* Unit tests.
* Development environments.
* Standalone scripts.
* Early project development.

The NullLogger acts as a safe fallback rather than a replacement for application logging.

---

## 6. Structured Logging

PythonTools supports structured logging patterns.

Typical operations include:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
```

Applications may expose additional capabilities beyond the standard logging interface.

PythonTools may also emit execution-oriented events such as:

```python
logger.command_start(...)

logger.command_end(...)

logger.command_error(...)
```

These events allow applications to consistently record execution activity.

The exact implementation remains application-defined.

---

## 7. Redaction

PythonTools should never log sensitive information.

Examples include:

* Passwords.
* Private keys.
* API tokens.
* Authentication credentials.
* Encryption keys.

If sensitive values must be referenced, applications should use redacted representations.

Example:

```text
********
```

or:

```text
[REDACTED]
```

Logging should provide operational visibility without disclosing secrets.

---

## 8. Responsibility Boundaries

PythonTools intentionally limits its logging responsibilities.

PythonTools is responsible for:

* Issuing log events.
* Providing logging interfaces.
* Supporting logger injection.
* Supporting NullLogger behavior.

PythonTools is not responsible for:

* Log file creation.
* Rotation policies.
* Retention policies.
* Storage locations.
* Alerting policies.
* Operational monitoring.

These responsibilities belong to the consuming application.

---

## 9. Stability Model

The logging interface is considered part of the PythonTools public API.

Logging enhancements may be added over time.

Existing logging behavior should remain stable whenever practical.

Breaking changes require a version increment.

Consuming applications should be able to upgrade PythonTools without rewriting logging integrations.

---

## 10. Summary

PythonTools provides a shared logging model for the Linktech Engineering ecosystem.

Key characteristics include:

* Logger injection.
* NullLogger fallback.
* Structured execution events.
* Secret redaction.
* Deterministic behavior.
* Application-controlled policy.

PythonTools records execution facts while applications retain complete control over logging strategy.

---

## 11. Notes

This document describes the logging architecture used by PythonTools.

For related information, see:

* [Caching.md](Caching.md)
* [Design.md](Design.md)
* [Sessions.md](Sessions.md)
* [Networking.md](Networking.md)
* [Weather.md](Weather.md)
* API_Reference.md
* Troubleshooting.md

Logging behavior documented here is intended to remain stable across all consuming applications.