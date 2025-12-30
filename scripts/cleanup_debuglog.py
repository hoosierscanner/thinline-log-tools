#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
import shutil
import tempfile
import re
import configparser
from pathlib import Path

CONFIG = Path.home() / ".thinline-log-tools" / "config.ini"

cfg = configparser.ConfigParser()
if not cfg.read(CONFIG):
    raise SystemExit(f"Config not found: {CONFIG}")

LOG_FILE = Path(cfg["paths"]["log_file"]).expanduser()
RETENTION_HOURS = int(cfg["cleanup"].get("retention_hours", "36"))

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)

TS_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+\]")

tmp = tempfile.NamedTemporaryFile(delete=False, mode="w")

with open(LOG_FILE, "r") as f:
    for line in f:
        m = TS_RE.search(line)
        if not m:
            tmp.write(line)
            continue

        ts = datetime.strptime(
            m.group(1),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        if ts >= CUTOFF:
            tmp.write(line)

tmp.close()
shutil.move(tmp.name, LOG_FILE)
