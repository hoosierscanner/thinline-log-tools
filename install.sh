#!/usr/bin/env bash
set -e

echo "ThinLine Log Tools Installer"
echo "----------------------------"

INSTALL_DIR="$HOME/.thinline-log-tools"

read -p "Debug log path [~/thinline-radio/tone-keyword-debug.log]: " LOG_FILE
LOG_FILE=${LOG_FILE:-"$HOME/thinline-radio/tone-keyword-debug.log"}

read -p "Cost output log [~/.thinline-log-tools/transcription_cost.log]: " STATS_LOG
STATS_LOG=${STATS_LOG:-"$INSTALL_DIR/transcription_cost.log"}

read -p "Model name [google-stt-standard]: " MODEL
MODEL=${MODEL:-"google-stt-standard"}

read -p "Cost per minute [0.024]: " COST
COST=${COST:-"0.024"}

read -p "Words per minute [150]: " WPM
WPM=${WPM:-"150"}

mkdir -p "$INSTALL_DIR/scripts"
cp scripts/*.py "$INSTALL_DIR/scripts/"

cat > "$INSTALL_DIR/config.ini" <<EOF2
[paths]
log_file = $LOG_FILE
stats_log = $STATS_LOG

[cleanup]
retention_hours = 36

[model]
name = $MODEL
cost_per_minute = $COST
words_per_minute = $WPM
EOF2

chmod +x "$INSTALL_DIR/scripts/"*.py

echo
echo "Installed to $INSTALL_DIR"
echo "Config written to $INSTALL_DIR/config.ini"
echo
echo "Test commands:"
echo "  python3 $INSTALL_DIR/scripts/cleanup_debuglog.py"
echo "  python3 $INSTALL_DIR/scripts/daily_transcription_stats.py"
