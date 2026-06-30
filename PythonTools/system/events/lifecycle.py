#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: lifecycle.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: Description of this module

"""
def record_event(summary, event, logger=None):
    summary["lifecycle_events"].append(event)
    if logger:
        logger.lifecycle(event)

