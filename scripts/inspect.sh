#!/bin/bash

# IntruderFound - Session Inspector

LOG_FILE="logs/session.log"
REPORT_FILE="reports/session_report.txt"

# Check whether the log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Session log not found."
    exit 1
fi

# Create reports directory if it does not exist
mkdir -p reports

# Generate the report
awk -F'|' '

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

    if (event == "SESSION_START")
    {
        session_count++
        start_time[session_id] = timestamp
    }

    else if (event == "SESSION_END")
    {
        end_time[session_id] = timestamp
    }

    else if (event == "COMMAND")
    {
        total_commands++

        command_text = details

        # Remove leading spaces
        sub(/^[ \t]+/, "", command_text)

        # Extract the command name
        split(command_text, parts, /[ \t]+/)

        if (parts[1] != "")
        {
            frequency[parts[1]]++
        }
    }

    else if (event == "SUSPICIOUS")
    {
        suspicious_count++

        suspicious_details[suspicious_count] = timestamp " | " session_id " | " details
    }

    else if (event == "SIGNAL")
    {
        signal_count++

        signal_details[signal_count] = timestamp " | " session_id " | " details
    }
}

END {
    print "=========================================="
    print "       INTRUDFOUND SESSION REPORT"
    print "=========================================="

    print ""
    print "SUMMARY"
    print "------------------------------------------"

    printf "Total sessions: %d\n", session_count
    printf "Total commands: %d\n", total_commands
    printf "Suspicious activities: %d\n", suspicious_count
    printf "Signal events: %d\n", signal_count

    print ""
    print "SUSPICIOUS ACTIVITY DETAILS"
    print "------------------------------------------"

    if (suspicious_count == 0)
    {
        print "No suspicious activities detected."
    }

    for (i = 1; i <= suspicious_count; i++)
    {
        printf "%d. %s\n", i, suspicious_details[i]
    }

    print ""
    print "COMMAND FREQUENCY"
    print "------------------------------------------"

    for (cmd in frequency)
    {
        printf "%-20s %d\n", cmd, frequency[cmd]
    }

    print ""
    print "SESSION DETAILS"
    print "------------------------------------------"

    for (id in start_time)
    {
        printf "Session ID: %s\n", id
        printf "Start time: %s\n", start_time[id]

        if (id in end_time)
        {
            printf "End time: %s\n", end_time[id]
        }
        else
        {
            print "End time: Session has no recorded end"
        }

        print ""
    }

    print "SIGNAL EVENTS"
    print "------------------------------------------"

    if (signal_count == 0)
    {
        print "No signal events recorded."
    }

    for (i = 1; i <= signal_count; i++)
    {
        printf "%d. %s\n", i, signal_details[i]
    }

    print ""
    print "=========================================="
    print "          END OF REPORT"
    print "=========================================="
}

' "$LOG_FILE" > "$REPORT_FILE"

echo "Session analysis completed successfully!"
echo "Report saved at: $REPORT_FILE"
echo ""
cat "$REPORT_FILE"
