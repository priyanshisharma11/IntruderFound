#!/bin/bash
# ==============================================================================
# IntruderFound - Session Inspector & Forensic Reporting Pipeline
# Course: UNIX Programming Lab (24B15CS214)
# Demonstrates: grep, sed, awk, loops, conditionals, traps, and Markdown export
# ==============================================================================

set -euo pipefail

LOG_FILE="logs/session.log"
REPORT_TXT="reports/session_report.txt"
REPORT_MD="reports/session_report.md"

# Ensure reports directory exists
mkdir -p reports

# Check whether the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "[-] Error: Session log file '$LOG_FILE' not found."
    exit 1
fi

# Set up temporary working files and a POSIX trap to guarantee cleanup
TMP_FILTERED=$(mktemp /tmp/intruderfound_filtered.XXXXXX)
TMP_SESSIONS=$(mktemp /tmp/intruderfound_sessions.XXXXXX)
trap 'rm -f "$TMP_FILTERED" "$TMP_SESSIONS"' EXIT INT TERM

# ------------------------------------------------------------------------------
# STEP 1: Filter and sanitize using GREP
# Exclude empty lines and comment lines, ensure minimum fields exist
# ------------------------------------------------------------------------------
grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\|' "$LOG_FILE" > "$TMP_FILTERED" || true

if [ ! -s "$TMP_FILTERED" ]; then
    echo "[-] No valid telemetry events found in '$LOG_FILE'."
    exit 0
fi

# ------------------------------------------------------------------------------
# STEP 2: Preprocess using SED
# Normalize spaces around delimiters
# ------------------------------------------------------------------------------
sed -E 's/[[:space:]]*\|[[:space:]]*/|/g' "$TMP_FILTERED" > "$TMP_SESSIONS"

# Helper function to convert "YYYY-MM-DD HH:MM:SS" to epoch seconds (Linux & macOS)
to_epoch() {
    local dt="$1"
    if date -j -f "%Y-%m-%d %H:%M:%S" "$dt" "+%s" 2>/dev/null; then
        return
    fi
    date -d "$dt" "+%s" 2>/dev/null || echo 0
}

# ------------------------------------------------------------------------------
# STEP 3: Process Telemetry using AWK
# ------------------------------------------------------------------------------
CURRENT_DATE=$(date "+%Y-%m-%d %H:%M:%S")

awk -F'|' -v cur_time="$CURRENT_DATE" '
BEGIN {
    total_commands = 0
    suspicious_count = 0
    signal_count = 0
    session_count = 0
}

{
    timestamp = $1
    session_id = $2
    event = $3
    details = $4

    if (event == "SESSION_START") {
        if (!(session_id in start_time)) {
            session_count++
            session_order[session_count] = session_id
        }
        start_time[session_id] = timestamp
    }
    else if (event == "SESSION_END") {
        end_time[session_id] = timestamp
    }
    else if (event == "COMMAND") {
        total_commands++
        cmd_text = details
        sub(/^[ \t]+/, "", cmd_text)
        split(cmd_text, parts, /[ \t]+/)
        base_cmd = parts[1]
        if (base_cmd != "") {
            frequency[base_cmd]++
        }
    }
    else if (event == "SUSPICIOUS") {
        suspicious_count++
        suspicious_records[suspicious_count] = timestamp "|" session_id "|" details
    }
    else if (event == "SIGNAL") {
        signal_count++
        signal_records[signal_count] = timestamp "|" session_id "|" details
    }
}

END {
    # --------------------------------------------------------------------------
    # Generate Plain Text Report
    # --------------------------------------------------------------------------
    print "======================================================================" > "'"$REPORT_TXT"'"
    print "                 INTRUDERFOUND FORENSIC SESSION REPORT                " > "'"$REPORT_TXT"'"
    print "======================================================================" > "'"$REPORT_TXT"'"
    print "" > "'"$REPORT_TXT"'"
    print "1. EXECUTIVE SUMMARY" > "'"$REPORT_TXT"'"
    print "----------------------------------------------------------------------" > "'"$REPORT_TXT"'"
    printf "Total Tracked Sessions   : %d\n", session_count > "'"$REPORT_TXT"'"
    printf "Total Commands Executed  : %d\n", total_commands > "'"$REPORT_TXT"'"
    printf "Suspicious Incidents     : %d\n", suspicious_count > "'"$REPORT_TXT"'"
    printf "Intercepted Signals      : %d\n", signal_count > "'"$REPORT_TXT"'"
    print "" > "'"$REPORT_TXT"'"

    print "2. SUSPICIOUS INCIDENTS & THREAT ALERTS" > "'"$REPORT_TXT"'"
    print "----------------------------------------------------------------------" > "'"$REPORT_TXT"'"
    if (suspicious_count == 0) {
        print "No suspicious activities detected." > "'"$REPORT_TXT"'"
    } else {
        for (i = 1; i <= suspicious_count; i++) {
            split(suspicious_records[i], r, "|")
            printf("[%02d] %s | Session: %s\n     Threat Classification: %s\n", i, r[1], r[2], r[3]) > "'"$REPORT_TXT"'"
        }
    }
    print "" > "'"$REPORT_TXT"'"

    print "3. COMMAND FREQUENCY DISTRIBUTION" > "'"$REPORT_TXT"'"
    print "----------------------------------------------------------------------" > "'"$REPORT_TXT"'"
    printf "%-20s %s\n", "Command", "Executions" > "'"$REPORT_TXT"'"
    printf "%-20s %s\n", "--------------------", "----------" > "'"$REPORT_TXT"'"
    for (cmd in frequency) {
        printf "%-20s %d\n", cmd, frequency[cmd] > "'"$REPORT_TXT"'"
    }
    print "" > "'"$REPORT_TXT"'"

    print "4. INTERCEPTED POSIX SIGNALS" > "'"$REPORT_TXT"'"
    print "----------------------------------------------------------------------" > "'"$REPORT_TXT"'"
    if (signal_count == 0) {
        print "No terminal interrupt signals intercepted." > "'"$REPORT_TXT"'"
    } else {
        for (i = 1; i <= signal_count; i++) {
            split(signal_records[i], s, "|")
            printf("[%02d] %s | Session: %s | %s\n", i, s[1], s[2], s[3]) > "'"$REPORT_TXT"'"
        }
    }
    print "" > "'"$REPORT_TXT"'"
    print "======================================================================" > "'"$REPORT_TXT"'"
    print "                             END OF REPORT                            " > "'"$REPORT_TXT"'"
    print "======================================================================" > "'"$REPORT_TXT"'"

    # --------------------------------------------------------------------------
    # Generate Structured Markdown Report (as specified in Synopsis)
    # --------------------------------------------------------------------------
    print "# IntruderFound: Attacker Session Forensic Report" > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    print "> **Course:** UNIX Programming Lab (24B15CS214)  " > "'"$REPORT_MD"'"
    print "> **Generated:** " cur_time "  " > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    print "## 1. Executive Summary" > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    print "| Metric | Count |" > "'"$REPORT_MD"'"
    print "| :--- | :--- |" > "'"$REPORT_MD"'"
    printf("| **Total Sessions** | `%d` |\n", session_count) > "'"$REPORT_MD"'"
    printf("| **Total Commands Executed** | `%d` |\n", total_commands) > "'"$REPORT_MD"'"
    printf("| **Suspicious / Malicious Incidents** | `%d` |\n", suspicious_count) > "'"$REPORT_MD"'"
    printf("| **Intercepted POSIX Signals** | `%d` |\n", signal_count) > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"

    print "## 2. Suspicious Threat Classifications" > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    if (suspicious_count == 0) {
        print "_No suspicious activities detected._\n" > "'"$REPORT_MD"'"
    } else {
        print "| # | Timestamp | Session ID | Threat Category |" > "'"$REPORT_MD"'"
        print "| :- | :--- | :--- | :--- |" > "'"$REPORT_MD"'"
        for (i = 1; i <= suspicious_count; i++) {
            split(suspicious_records[i], r, "|")
            printf("| %d | `%s` | `%s` | **%s** |\n", i, r[1], r[2], r[3]) > "'"$REPORT_MD"'"
        }
        print "" > "'"$REPORT_MD"'"
    }

    print "## 3. Command Frequency Distribution" > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    print "| Command | Invocations |" > "'"$REPORT_MD"'"
    print "| :--- | :--- |" > "'"$REPORT_MD"'"
    for (cmd in frequency) {
        printf("| `%s` | %d |\n", cmd, frequency[cmd]) > "'"$REPORT_MD"'"
    }
    print "" > "'"$REPORT_MD"'"

    print "## 4. Signal Interceptions" > "'"$REPORT_MD"'"
    print "" > "'"$REPORT_MD"'"
    if (signal_count == 0) {
        print "_No signals intercepted._\n" > "'"$REPORT_MD"'"
    } else {
        print "| # | Timestamp | Signal Detail |" > "'"$REPORT_MD"'"
        print "| :- | :--- | :--- |" > "'"$REPORT_MD"'"
        for (i = 1; i <= signal_count; i++) {
            split(signal_records[i], s, "|")
            printf("| %d | `%s` | `%s` |\n", i, s[1], s[3]) > "'"$REPORT_MD"'"
        }
        print "" > "'"$REPORT_MD"'"
    }
}
' "$TMP_SESSIONS"

# ------------------------------------------------------------------------------
# STEP 4: Calculate Session Durations in Bash & Append to Reports
# ------------------------------------------------------------------------------
{
    echo ""
    echo "5. SESSION TIMELINE & DURATION"
    echo "----------------------------------------------------------------------"
} >> "$REPORT_TXT"

{
    echo "## 5. Session Timeline & Durations"
    echo ""
    echo "| Session ID | Start Time | End Time | Duration | Status |"
    echo "| :--- | :--- | :--- | :--- | :--- |"
} >> "$REPORT_MD"

# Parse start and end timestamps per session
awk -F'|' '$3 == "SESSION_START" { print "START|" $2 "|" $1 } $3 == "SESSION_END" { print "END|" $2 "|" $1 }' "$TMP_SESSIONS" > "$TMP_FILTERED"

# Compute durations per session
unique_sids=$(awk -F'|' '{print $2}' "$TMP_FILTERED" | sort -u)

for sid in $unique_sids; do
    start_ts=$(grep -E "^START\\|$sid\\|" "$TMP_FILTERED" | head -n 1 | cut -d'|' -f3 || true)
    end_ts=$(grep -E "^END\\|$sid\\|" "$TMP_FILTERED" | tail -n 1 | cut -d'|' -f3 || true)

    if [ -n "$start_ts" ] && [ -n "$end_ts" ]; then
        s_epoch=$(to_epoch "$start_ts")
        e_epoch=$(to_epoch "$end_ts")
        diff=$(( e_epoch - s_epoch ))
        if [ "$diff" -lt 0 ]; then diff=0; fi
        mins=$(( diff / 60 ))
        secs=$(( diff % 60 ))
        dur_str="${mins}m ${secs}s"
        status="Completed"
    elif [ -n "$start_ts" ]; then
        end_ts="Active / Terminated unexpectedly"
        dur_str="N/A"
        status="Incomplete"
    else
        start_ts="Unknown"
        dur_str="N/A"
        status="Corrupted"
    fi

    printf "Session: %s\n  Start   : %s\n  End     : %s\n  Duration: %s (%s)\n\n" \
        "$sid" "$start_ts" "$end_ts" "$dur_str" "$status" >> "$REPORT_TXT"

    printf "| \`%s\` | \`%s\` | \`%s\` | **%s** | %s |\n" \
        "$sid" "$start_ts" "$end_ts" "$dur_str" "$status" >> "$REPORT_MD"
done

echo "[+] Forensic reports successfully generated:"
echo "    - Text Report    : $REPORT_TXT"
echo "    - Markdown Report: $REPORT_MD"
echo ""
cat "$REPORT_TXT"
