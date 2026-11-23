# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-11-23
 Modified: 2026-11-23
 File: PythonTools/gui/monitors.py
 Version: 1.0.0
 Description: Helpers for displaying on Monitors
"""

from PySide6.QtGui import QCursor, QGuiApplication


def center_on_active_monitor(widget):
    """
    Center a QWidget/QMainWindow on the monitor
    currently containing the mouse cursor.
    """

    screens = QGuiApplication.screens()

    if len(screens) > 1:
        screen = QGuiApplication.screenAt(
            QCursor.pos()
        )

        if screen:
            geo = screen.availableGeometry()

            x = geo.x() + (
                geo.width() - widget.width()
            ) // 2

            y = geo.y() + (
                geo.height() - widget.height()
            ) // 2

            widget.move(x, y)
            return

    screen = QGuiApplication.primaryScreen()

    if not screen:
        return

    geo = screen.availableGeometry()

    if (
        len(screens) == 1
        and geo.width() > 3000
    ):
        cursor = QCursor.pos()

        monitor_width = geo.width() // 2

        monitor_index = (
            cursor.x() // monitor_width
        )

        monitor_x = (
            geo.x()
            + monitor_index * monitor_width
        )

        x = monitor_x + (
            monitor_width - widget.width()
        ) // 2

        y = geo.y() + (
            geo.height() - widget.height()
        ) // 2

        widget.move(x, y)
        return

    x = geo.x() + (
        geo.width() - widget.width()
    ) // 2

    y = geo.y() + (
        geo.height() - widget.height()
    ) // 2

    widget.move(x, y)