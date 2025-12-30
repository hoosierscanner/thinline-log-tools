#!/usr/bin/env python3
import re
from datetime import datetime, timezone
import configparser
from pathlib import Path

CONFIG = Path.home() / ".thinline-log-tools" / "config.ini"

cfg = configparser.ConfigParser()
if not cfg.read(CONFIG):
    raise SystemExit(f"Config not found: {CONFIG}")

LOG_FILE = Path(cfg["paths"]["log_file"]).expanduser()
STATS_LOG = Path(cfg["paths"]["stats_log"]).expanduser()

MODEL = cfg["model"].get("name", "google-stt-standard")
COST_PER_MIN = float(cfg["model"].get("cost_per_minute", "0.024"))
WPM = int(cfg["model"].get("words_per_minute", "150"))

EXCLUDED = {"VOICE_CHECK", "NOT_VOICE", "VOICE"}

TRANSCRIPT_RE = re.compile(r'Transcript:\s*"([^"]+)"')
CAPS_WORD_RE = re.compile(r"\b[A-Z]{2,}\b")

word_count = 0

with open(LOG_FILE, "r") as f:
    for line in f:
        m = TRANSCRIPT_RE.search(line)
        if not m:
            continue
        for w in CAPS_WORD_RE.findall(m.group(1)):
            if w not in EXCLUDED:
                word_count += 1

minutes = word_count / WPM if WPM else 0.0
cost = minutes * COST_PER_MIN

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

STATS_LOG.parent.mkdir(parents=True, exist_ok=True)

with open(STATS_LOG, "a") as out:
    out.write(
        f"{ts} | model={MODEL} | words={word_count} | "
        f"minutes={minutes:.2f} | cost=${cost:.4f}\n"
    )
