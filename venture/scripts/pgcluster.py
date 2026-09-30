"""Start/stop an ephemeral local PostgreSQL cluster for development and tests.

Usage:
  python scripts/pgcluster.py start <dir> <port>   # prints admin URL
  python scripts/pgcluster.py stop <dir>
When running as root, the cluster runs as the 'postgres' OS user (initdb refuses root).
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import time


def _bindir() -> str:
    for cand in sorted(glob.glob("/usr/lib/postgresql/*/bin"), reverse=True):
        if os.path.exists(os.path.join(cand, "initdb")):
            return cand
    found = shutil.which("initdb")
    if found:
        return os.path.dirname(found)
    raise SystemExit("PostgreSQL server binaries (initdb) not found")


def _run(cmd: list[str]) -> None:
    if os.geteuid() == 0:
        cmd = ["runuser", "-u", "postgres", "--", *cmd]
    # Fixed argument vectors built in this module (no shell, no user input).
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)  # noqa: S603
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr}")


def start(datadir: str, port: int) -> str:
    b = _bindir()
    if not os.path.exists(os.path.join(datadir, "PG_VERSION")):
        os.makedirs(datadir, exist_ok=True)
        if os.geteuid() == 0:
            shutil.chown(datadir, "postgres", "postgres")
        _run([f"{b}/initdb", "-D", datadir, "-U", "pgadmin", "--auth=trust", "-E", "UTF8", "--no-locale"])
    sockdir = os.path.join(datadir, "sock")
    os.makedirs(sockdir, exist_ok=True)
    if os.geteuid() == 0:
        shutil.chown(sockdir, "postgres", "postgres")
    _run(
        [
            f"{b}/pg_ctl",
            "-D",
            datadir,
            "-l",
            os.path.join(datadir, "log.txt"),
            "-w",
            "-o",
            f"-p {port} -k {sockdir} -c listen_addresses=127.0.0.1 -c fsync=off -c full_page_writes=off",
            "start",
        ]
    )
    time.sleep(0.2)
    return f"postgresql+psycopg://pgadmin@127.0.0.1:{port}/postgres"


def stop(datadir: str) -> None:
    b = _bindir()
    _run([f"{b}/pg_ctl", "-D", datadir, "-m", "fast", "-w", "stop"])


if __name__ == "__main__":
    if sys.argv[1] == "start":
        print(start(sys.argv[2], int(sys.argv[3])))
    elif sys.argv[1] == "stop":
        stop(sys.argv[2])
