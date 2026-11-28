# PythonTools Sessions

**Part of:** Linktech Engineering Tools Suite  
**Document:** Sessions  
**Author:** Leon McClatchey, Linktech Engineering LLC  
**License:** MIT  
**Requires:** PythonTools  
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Session Philosophy](#3-session-philosophy)
4. [Session Types](#4-session-types)
   1. [Local Sessions](#41-local-sessions)
   2. [Privileged Local Sessions](#42-privileged-local-sessions)
   3. [SSH Sessions](#43-ssh-sessions)
5. [Authentication Model](#5-authentication-model)
6. [Return Structure](#6-return-structure)
7. [Logging Integration](#7-logging-integration)
8. [Responsibility Boundaries](#8-responsibility-boundaries)
9. [Stability Model](#9-stability-model)
10. [Summary](#10-summary)
11. [Notes](#11-notes)

---

## 1. Overview

PythonTools provides a unified session and execution model for local and remote command execution.

The session layer abstracts platform-specific execution details while providing a consistent interface to consuming applications.

All session types aim to provide deterministic behavior, structured results, and consistent error handling.

---

## 2. Purpose

The session subsystem exists to:

* Execute commands.
* Manage SSH connectivity.
* Normalize execution results.
* Standardize error handling.
* Integrate with application logging.
* Eliminate duplicate execution logic.

Applications can focus on operational behavior while PythonTools manages execution mechanics.

---

## 3. Session Philosophy

PythonTools follows several session design principles.

### Deterministic

Session execution should produce consistent and predictable results.

### Unified

All execution mechanisms should return similar structures and follow similar behavioral patterns.

### Application-Agnostic

Sessions execute commands but do not interpret command results.

### Structured

Execution results should be returned in a consistent and machine-readable format.

### Observable

Session activity should support logging and troubleshooting.

---

## 4. Session Types

PythonTools supports multiple execution methods.

### 4.1 Local Sessions

Local sessions execute commands directly on the current system.

Example:

```python
result = local_command("ls -la")
```

Typical use cases include:

* Diagnostics
* Environment inspection
* Non-privileged execution
* Local tooling

Local execution does not require SSH connectivity.

---

### 4.2 Privileged Local Sessions

Privileged local sessions execute commands using elevated privileges.

Example:

```python
result = sudo_run("zypper refresh")
```

Characteristics include:

* Password injection support.
* Captured output.
* Captured exit codes.
* Structured results.

Privileged execution is commonly used when administrative access is required.

---

### 4.3 SSH Sessions

SSHSession provides remote execution capabilities.

Example:

```python
session = SSHSession(
    address="192.0.2.10",
    port=2222,
    username="admin",
    keyfile="/path/to/key"
)

result = session.run("zypper refresh")
```

SSHSession manages:

* Connection establishment.
* Session lifecycle.
* Command execution.
* Output collection.
* Exit-code retrieval.
* Error normalization.

Remote execution uses the same result model as local execution whenever practical.

---

## 5. Authentication Model

PythonTools supports multiple authentication mechanisms.

Supported methods include:

* SSH key authentication.
* Password authentication.
* Sudo password injection.

Authentication preference is typically:

1. SSH key
2. Password

Applications supply credentials through secret injection mechanisms.

PythonTools consumes credentials but does not own credential management.

---

## 6. Return Structure

Session operations return a normalized structure.

Example:

```python
{
    "stdout": "...",
    "stderr": "...",
    "exit_code": 0,
    "ok": True
}
```

Benefits include:

* Consistency.
* Predictability.
* Easier debugging.
* Simplified application integration.

Applications interpret execution results.

PythonTools reports execution facts.

---

## 7. Logging Integration

The session subsystem integrates with the PythonTools logging model.

Typical events include:

```python
logger.command_start(...)

logger.command_end(...)

logger.command_error(...)
```

Session execution should generate meaningful operational events without exposing sensitive information.

Logging implementation remains application-controlled.

---

## 8. Responsibility Boundaries

PythonTools is responsible for:

* Command execution.
* SSH connectivity.
* Output collection.
* Exit-code retrieval.
* Error normalization.
* Session lifecycle management.

PythonTools is not responsible for:

* Update orchestration.
* Monitoring policy.
* Command interpretation.
* Workflow decisions.
* Business logic.

These responsibilities belong to consuming applications.

---

## 9. Stability Model

Session interfaces are considered part of the PythonTools public API.

The following guarantees apply:

* Existing functionality should remain stable.
* New capabilities may be added.
* Breaking changes require a version increment.
* Return structures should remain consistent.

Applications should be able to upgrade PythonTools without significant session-layer changes.

---

## 10. Summary

PythonTools provides a unified execution model through local, privileged, and remote session types.

Key characteristics include:

* Deterministic behavior.
* Structured results.
* Consistent execution patterns.
* SSH integration.
* Logging integration.
* Application independence.

The session subsystem provides execution capabilities while leaving operational decisions to consuming applications.

---

## 11. Notes

This document describes the session architecture used by PythonTools.

For related information, see:

* [Caching.md](Caching.md)
* [Design.md](Design.md)
* [Logging.md](Logging.md)
* [Networking.md](Networking.md)
* [Weather.md](Weather.md)
* API_Reference.md
* Troubleshooting.md

Session behavior documented here is intended to remain stable across all consuming applications.