# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-23
 Modified: 2026-05-23
 File: PythonTools/sessions/systemd_runner.py
 Version: 1.0.0
 Description: 
        Helper for running commands via systemd-run, locally or over SSH.
        Depends on a session object with:
        result = session.run(cmd: str, use_sudo: bool = False)
        where result has: stdout, stderr, returncode (or code), msg.
"""

import shlex
import time
from types import SimpleNamespace


class SystemdRunner:
    """
    Generic systemd-run wrapper.

    Uses an existing session (LocalSession, SSHSession, etc.) to:
      - start a transient unit with systemd-run
      - poll its status via systemctl show
      - fetch logs via journalctl
    """

    def __init__(self, session, logger=None, hostname=None, poll_interval=2.0):
        """
        :param session: LocalSession or SSHSession (must provide .run(cmd, use_sudo=False/True))
        :param logger: Optional logger
        :param hostname: Optional hostname (for logging / unit naming)
        :param poll_interval: Seconds between status polls
        """
        self.session = session
        self.logger = logger
        self.hostname = hostname or "host"
        self.poll_interval = poll_interval

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    def _log(self, level, msg):
        if self.logger:
            getattr(self.logger, level, self.logger.info)(msg)

    def _exec(self, cmd: str, use_sudo: bool = True):
        """
        Execute a command via the underlying session.
        Default is sudo because systemd operations are usually privileged.
        """
        self._log("debug", f"[SystemdRunner] exec (sudo={use_sudo}): {cmd}")
        result = self.session.run(cmd, use_sudo=use_sudo)

        # Normalize returncode field name
        code = getattr(result, "returncode", getattr(result, "code", 0))
        stdout = getattr(result, "stdout", getattr(result, "msg", ""))
        stderr = getattr(result, "stderr", getattr(result, "err", ""))

        self._log("debug", f"[SystemdRunner] code={code}, stdout={stdout}, stderr={stderr}")

        return SimpleNamespace(
            stdout=stdout,
            stderr=stderr,
            returncode=code,
            code=code,
            msg=stdout,
        )

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def run(self, command: str, unit: str | None = None, description: str | None = None):
        """
        Start a transient systemd unit with systemd-run.

        :param command: The actual command to run (e.g. 'zypper update -y')
        :param unit: Optional explicit unit name; if None, one is generated.
        :param description: Optional Description= for the unit.
        :return: unit_name (str)
        """
        unit_name = unit or f"runupdates-{self.hostname}"

        desc = description or f"RunUpdates job on {self.hostname}"
        desc_quoted = shlex.quote(desc)

        # We send the actual payload command as a single shell string.
        cmd_quoted = command

        systemd_cmd = (
            f"systemd-run "
            f"--unit={shlex.quote(unit_name)} "
            f"--description={desc_quoted} "
            f"--collect "
            f"-p StandardOutput=journal "
            f"-p StandardError=journal "
            f"/bin/sh -c {shlex.quote(cmd_quoted)}"
        )

        self._log("info", f"[SystemdRunner] Starting unit {unit_name}: {command}")
        result = self._exec(systemd_cmd, use_sudo=True)

        if result.returncode != 0:
            raise RuntimeError(f"systemd-run failed for unit {unit_name}: {result.stderr or result.stdout}")

        return unit_name

    def poll(self, unit: str):
        """
        Poll systemd for unit status.

        :return: SimpleNamespace(result=<str>, status=<int>, raw=<stdout>)
                 where status is ExecMainStatus (int) or None if not present.
        """
        cmd = f"systemctl show {shlex.quote(unit)} -p Result -p ExecMainStatus -p ActiveState"
        result = self._exec(cmd, use_sudo=True)

        if result.returncode != 0:
            # Unit may have been GC'd or never existed
            self._log("warning", f"[SystemdRunner] systemctl show failed for {unit}: {result.stderr}")
            return SimpleNamespace(result="unknown", status=None, raw=result.stdout)

        raw = result.stdout.strip().splitlines()
        data = {}
        for line in raw:
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()

        res = data.get("Result", "unknown")
        try:
            status = int(data.get("ExecMainStatus", "0"))
        except ValueError:
            status = None

        self._log("debug", f"[SystemdRunner] poll {unit}: Result={res}, ExecMainStatus={status}")
        return SimpleNamespace(result=res, status=status, raw=result.stdout)

    def logs(self, unit: str, lines: int | None = None):
        """
        Fetch journald logs for the unit.

        :param unit: Unit name
        :param lines: Optional max lines (if None, full log)
        :return: stdout (str)
        """
        tail = f"-n {int(lines)} " if lines is not None else ""
        cmd = f"journalctl -u {shlex.quote(unit)} {tail}--no-pager"
        result = self._exec(cmd, use_sudo=True)

        if result.returncode != 0:
            self._log("warning", f"[SystemdRunner] journalctl failed for {unit}: {result.stderr}")
        return result.stdout

    def run_and_wait(
        self,
        command: str,
        unit: str | None = None,
        description: str | None = None,
        timeout: int = 900,
    ):
        """
        High-level helper: start a unit, poll until completion, then fetch logs.

        :return: SimpleNamespace(
                    unit=<str>,
                    result=<str>,          # systemd Result= (e.g. 'success', 'exit-code')
                    status=<int|None>,     # ExecMainStatus
                    logs=<str>,            # journald output
                    success=<bool>,
                )
        """
        unit_name = self.run(command, unit=unit, description=description)

        start = time.time()
        last_state = None

        while True:
            info = self.poll(unit_name)
            last_state = info

            # Result=success or failure is set when the unit is done.
            if info.result not in ("unknown", ""):
                break

            if (time.time() - start) > timeout:
                self._log("error", f"[SystemdRunner] Timeout waiting for unit {unit_name}")
                break

            time.sleep(self.poll_interval)

        log_text = self.logs(unit_name)

        success = (last_state.result == "success") and (last_state.status == 0)

        self._log(
            "info",
            f"[SystemdRunner] Completed unit {unit_name}: "
            f"Result={last_state.result}, ExecMainStatus={last_state.status}, success={success}",
        )

        return SimpleNamespace(
            unit=unit_name,
            result=last_state.result,
            status=last_state.status,
            logs=log_text,
            success=success,
        )

