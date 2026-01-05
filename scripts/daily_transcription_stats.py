#!/usr/bin/env python3
"""
Daily transcription cost estimation based on VOICE_CHECK transcripts.

Assumptions:
- Transcripts are already normalized to ALL CAPS by upstream processing
- Only VOICE_CHECK transcript lines are relevant
- Words include:
    * ALL CAPS tokens
    * Numbers (unit IDs, addresses, codes)
    * Single-letter words (e.g., 'A')
- Punctuation and lowercase noise are ignored
"""

import os
import re
from datetime import datetime, timezone
import configparser
from pathlib import Path

# ------------------------------------------------------------
# Config loading
# ------------------------------------------------------------
# Allow an environment override for flexibility (cron, testing, repo-local use),
# but default to the standard user install location.
CONFIG = Path(
    os.environ.get(
        "THINLINE_CONFIG",
        Path.home() / ".thinline-log-tools" / "config.ini"
    )
)

cfg = configparser.ConfigParser()

# Fail fast if config is missing — this should never silently succeed
if not cfg.read(CONFIG):
    raise SystemExit(f"Config not found: {CONFIG}")

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
# Debug log produced by tone / VOICE_CHECK processing
LOG_FILE = Path(cfg["paths"]["log_file"]).expanduser()

# Output log where cost estimates are appended
STATS_LOG = Path(cfg["paths"]["stats_log"]).expanduser()

# ------------------------------------------------------------
# Model / costing parameters
# ------------------------------------------------------------
MODEL = cfg["model"].get("name", "google-stt-standard")

try:
    COST_PER_MIN = float(cfg["model"].get("cost_per_minute", "0.024"))
    WPM = int(cfg["model"].get("words_per_minute", "150"))
except ValueError as e:
    raise SystemExit(f"Invalid numeric config value: {e}")

# ------------------------------------------------------------
# Parsing rules
# ------------------------------------------------------------
# VOICE_CHECK emits transcripts inside quoted "Transcript: " fields
TRANSCRIPT_RE = re.compile(r'Transcript:\s*"([^"]*)"')

# Count words as VOICE_CHECK does:
# - ALL CAPS tokens
# - Numbers (addresses, unit IDs)
# - Single-letter words
# - Ignore punctuation automatically via word boundaries
WORD_RE = re.compile(r"\b[A-Z0-9]{1,}\b")

# Tokens that appear in logs but should never count as spoken words
EXCLUDED = {
    "VOICE_CHECK",
    "NOT_VOICE",
    "VOICE",
}

# ------------------------------------------------------------
# Word counting
# ------------------------------------------------------------
if not LOG_FILE.exists():
    raise SystemExit(f"Log file not found: {LOG_FILE}")

word_count = 0

with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        match = TRANSCRIPT_RE.search(line)
        if not match:
            continue

        transcript = match.group(1)

        # Empty transcripts are common and intentional — skip quietly
        if not transcript:
            continue

        for token in WORD_RE.findall(transcript):
            if token not in EXCLUDED:
                word_count += 1

# ------------------------------------------------------------
# Cost calculation
# ------------------------------------------------------------
# Protect against divide-by-zero if WPM is misconfigured
minutes = word_count / WPM if WPM > 0 else 0.0
cost = minutes * COST_PER_MIN

# Timestamp in UTC for consistency across hosts
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------
# Ensure log directory exists
STATS_LOG.parent.mkdir(parents=True, exist_ok=True)

with STATS_LOG.open("a", encoding="utf-8") as out:
    out.write(
        f"{timestamp} | model={MODEL} | "
        f"words={word_count} | minutes={minutes:.2f} | "
        f"cost=${cost:.4f}\n"
    )
