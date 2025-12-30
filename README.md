# thinline-log-tools
Debug log clean up and cloud transcription cost estimation

Lightweight helper tools for **ThinLine Radio** that:

1. Automatically clean up debug logs (time-based retention)
2. Estimate speech-to-text API usage and cost from transcription output

This project is intentionally:
- Small
- Dependency-free (standard Python + Bash)
- Config-driven
- Safe to run unattended via cron

---

## What this project does

### 1) Log cleanup (hourly)

ThinLine’s `tone-keyword-debug.log` can grow quickly and indefinitely.

The cleanup script:
- Parses timestamps from each log line
- Keeps only entries newer than a configured retention window (default: **36 hours**)
- Preserves headers and non-timestamp lines
- Rewrites the log safely using a temporary file

This prevents:
- Disk bloat
- Slow tailing / searching
- Unbounded log growth on long-running VPS installs

---

### 2) Transcription cost estimation (daily)

ThinLine logs include rejected and accepted transcription attempts, for example:

Transcript: "INDIANAPOLIS 5210."
Transcript: "08."

The cost script:
- Extracts only the `Transcript:` field
- Counts **ALL-CAPS words** (actual speech content)
- Excludes system markers:
  - VOICE_CHECK
  - NOT_VOICE
  - VOICE
- Converts words → minutes using a configurable WPM average
- Applies a configurable **cost-per-minute**
- Appends a daily summary to a cost log

This provides:
- Daily estimated usage
- Long-term cost trends
- A sanity check against cloud billing dashboards

---

## Supported speech-to-text models

Only the following providers are currently supported by the cost model logic.

Pricing reflects public list pricing as of **12/31 (USD)**.  
Always verify against your provider’s billing console.

### Current model pricing (as of 12/31)

Provider: Google Cloud  
Model name: `google-stt-standard`  
Approx cost: **$0.024 per minute**  
Notes: Standard Speech-to-Text (non-medical)

Provider: Azure Speech  
Model name: `azure-speech-standard`  
Approx cost: **$0.016–$0.018 per minute**  
Notes: Roughly $1.00–$1.08 per audio hour

Provider: AssemblyAI  
Model name: `assemblyai-standard`  
Approx cost: **$0.015 per minute**  
Notes: Standard real-time or batch tier

### Why cost is configurable

Pricing is not hard-coded because:
- Vendor rates change
- Discounts and committed-use pricing vary
- Conservative estimates may be preferred

You can adjust:
- Model name (label only)
- Cost per minute
- Words-per-minute assumption

All without changing code.

---

## Repository layout

thinline-log-tools/
├── README.md
├── install.sh
├── config/
│   └── config.ini.template
└── scripts/
    ├── cleanup_debuglog.py
    └── daily_transcription_stats.py

---

## Installation

### 1) Clone or copy the repository

git clone <repo-url>  
cd thinline-log-tools

---

### 2) Run the installer

./install.sh

You’ll be prompted for:
- Debug log path  
  Default: `~/thinline-radio/tone-keyword-debug.log`
- Cost output log  
  Default: `~/.thinline-log-tools/transcription_cost.log`
- Model name (label only)
- Cost per minute
- Words per minute (default: 150)

The installer will:
- Create `~/.thinline-log-tools/`
- Copy scripts into `~/.thinline-log-tools/scripts/`
- Generate `config.ini`
- Set executable permissions

---

## Configuration

After install, configuration lives here:

~/.thinline-log-tools/config.ini

Example:

[paths]  
log_file = ~/thinline-radio/tone-keyword-debug.log  
stats_log = ~/.thinline-log-tools/transcription_cost.log  

[cleanup]  
retention_hours = 36  

[model]  
name = google-stt-standard  
cost_per_minute = 0.024  
words_per_minute = 150  

You can edit this file at any time.  
No reinstall required.

---

## Manual testing (recommended)

Before enabling cron, run each script manually:

python3 ~/.thinline-log-tools/scripts/cleanup_debuglog.py  
python3 ~/.thinline-log-tools/scripts/daily_transcription_stats.py  

Then check output:

tail -n 5 ~/.thinline-log-tools/transcription_cost.log

Example output:

2025-12-31 00:00:00 UTC | model=google-stt-standard | words=499 | minutes=3.33 | cost=$0.0798

---

## Cron setup (important)

### Hourly cleanup

0 * * * * /usr/bin/python3 ~/.thinline-log-tools/scripts/cleanup_debuglog.py

### Daily cost estimation

0 0 * * * /usr/bin/python3 ~/.thinline-log-tools/scripts/daily_transcription_stats.py

### Install cron jobs

crontab -e

Paste both entries, save, then verify:

crontab -l

---

## Design assumptions and limitations

- Logs follow ThinLine’s standard debug format
- Timestamps are UTC
- Transcription content appears in Transcript fields
- Cost estimates are approximate, not billing-authoritative
- Short clips and silence may still be billable by providers

This tool is intended for:
- Visibility
- Trend analysis
- Cost awareness

Not invoice reconciliation.

---

## Why this project exists

Cloud speech costs often:
- Hide in the background
- Scale quietly
- Surprise people later

This provides:
- A local, provider-agnostic estimate
- Zero vendor SDKs
- Zero external dependencies
- Clear numbers you can explain to finance or leadership

---

---

## License

Internal / private use unless otherwise specified.  
No warranty expressed or implied.
