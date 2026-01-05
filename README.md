# thinline-log-tools

Debug log cleanup and cloud transcription cost estimation

Lightweight helper tools for ThinLine Radio that:

1. Automatically clean up debug logs using time-based retention
2. Estimate speech-to-text API usage and cost from transcription output

This project is intentionally:

- Small
- Dependency-free (standard Python and Bash only)
- Config-driven
- Safe to run unattended via cron

---

## What this project does

### 1) Log cleanup (hourly)

ThinLine’s tone-keyword-debug.log can grow quickly and indefinitely.

The cleanup script:

- Parses timestamps from each log line
- Keeps only entries newer than a configured retention window (default: 36 hours)
- Preserves headers and non-timestamp lines
- Rewrites the log safely using a temporary file

This prevents:

- Disk bloat
- Slow tailing or searching
- Unbounded log growth on long-running VPS installs

---

### 2) Transcription cost estimation (daily)

ThinLine debug logs include rejected and accepted transcription attempts, for example:

Transcript: "INDIANAPOLIS 5210."
Transcript: "08."

The cost estimation script:

- Extracts only the Transcript field from log lines
- Counts spoken-word tokens from ALL-CAPS transcripts
  - Includes numbers and single-letter words
  - Ignores punctuation and lowercase noise
- Excludes system markers:
  - VOICE_CHECK
  - NOT_VOICE
  - VOICE
- Converts words to minutes using a configurable words-per-minute average
- Applies a configurable cost-per-minute value
- Appends a daily summary to a local cost log

This provides:

- Daily estimated usage
- Long-term cost trends
- A sanity check against cloud billing dashboards

---

## Supported speech-to-text models

This project does not integrate with vendor SDKs or APIs.

Model support here means:

- A label for reporting purposes
- A configurable cost-per-minute assumption

Pricing reflects public list pricing as of 12/31 (USD).
Always verify against your provider’s billing console.

### Example model pricing (as of 12/31)

Google Cloud
Model name: google-stt-standard
Approximate cost: $0.024 per minute
Notes: Standard Speech-to-Text (non-medical)

Azure Speech
Model name: azure-speech-standard
Approximate cost: $0.016–$0.018 per minute
Notes: Roughly $1.00–$1.08 per audio hour

AssemblyAI
Model name: assemblyai-standard
Approximate cost: $0.015 per minute

---

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
Repository (git-tracked)

thinline-log-tools
├── README.md
├── install.sh
├── .gitignore
├── logs
│ └── .gitkeep
├── config
│ └── config.ini.template
└── scripts
├── cleanup_debuglog.py
└── daily_transcription_stats.py

Repo-local logs (git-ignored)

thinline-log-tools/logs
└── transcription_cost.log

Runtime configuration and scripts (dot directory)

~/.thinline-log-tools
├── config.ini
├── scripts
│ ├── cleanup_debuglog.py
│ └── daily_transcription_stats.py

Source code lives in the repository.
Runtime configuration lives in ~/.thinline-log-tools/.
Logs are written to the repo-local logs directory and ignored by git.

---

## Installation

### 1) Clone the repository

Clone the repository and change into the directory.

### 2) Run the installer

Run ./install.sh

You will be prompted for:

- Debug log path
  Default: ~/thinline-radio/tone-keyword-debug.log
- Cost output log
  Default: ./logs/transcription_cost.log
- Model name (label only)
- Cost per minute
- Words per minute (default: 150)

The installer will:

- Create ~/.thinline-log-tools/
- Copy scripts into ~/.thinline-log-tools/scripts/
- Generate config.ini
- Set executable permissions

---

## Configuration

After installation, configuration lives at:

~/.thinline-log-tools/config.ini

Example configuration:

[paths]
log_file = ~/thinline-radio/tone-keyword-debug.log
stats_log = ~/thinline-log-tools/logs/transcription_cost.log

[cleanup]
retention_hours = 36

[model]
name = google-stt-standard
cost_per_minute = 0.024
words_per_minute = 150

You can edit this file at any time.
No reinstall is required.

---

## Manual testing (recommended)

Before enabling cron, run each script manually.

Run the cleanup script, then run the transcription cost script.

Afterward, check output by viewing the cost log in the logs directory.

Example output line:

2025-12-31 00:00:00 UTC | model=google-stt-standard | words=499 | minutes=3.33 | cost=$0.0798

---

## Cron setup

### Hourly cleanup

Run the cleanup script once per hour using cron.

### Daily cost estimation

Run the cost estimation script once per day, typically at midnight UTC.

After adding cron entries, verify them using crontab -l.

---

## Design assumptions and limitations

- Logs follow ThinLine’s standard debug format
- Timestamps are UTC
- Transcription content appears in Transcript fields
- Cost estimates are approximate and not billing-authoritative
- Short clips and silence may still be billable by providers

This tool is intended for:

- Visibility
- Trend analysis
- Cost awareness

It is not intended for invoice reconciliation.

---

## Why this project exists

Cloud speech costs often:

- Hide in the background
- Scale quietly
- Surprise people later

This project provides:

- A local, provider-agnostic estimate
- Zero vendor SDKs
- Zero external dependencies
- Clear numbers you can explain to leadership or finance

---

## License

Internal or private use unless otherwise specified.
No warranty expressed or implied.
