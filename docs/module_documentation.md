# INTRUDERFOUND – MODULE DOCUMENTATION

## 1. Introduction

IntruderFound is an interactive command-line honeypot simulation developed using C programming and Bash scripting. It provides a simulated terminal environment to demonstrate command execution, virtual file management, suspicious command detection, session logging, and signal handling.

The project is divided into different modules, each responsible for a specific functionality.

## 2. Main Module – main.c

The main.c file controls the overall execution of the IntruderFound application.

Responsibilities:
- Displays the welcome banner.
- Initializes the virtual file system.
- Starts session logging.
- Initializes signal handling.
- Accepts commands from the simulated user.
- Processes commands through the shell.
- Detects suspicious commands.
- Ends the session when the user enters the exit command.

## 3. Editor Module – editor.c and editor.h

The editor module implements a basic simulated VI text editor.

Responsibilities:
- Opens a virtual file for editing.
- Displays the existing file content.
- Supports NORMAL MODE and INSERT MODE.
- Allows users to enter text.
- Supports save and quit commands.
- Updates the virtual file content when saved.

The editor supports commands such as i, ESC, :w, :q, :wq, and :q!.

## 4. Logger Module – logger.c and logger.h

The logger module records activities performed during a simulated session.

Responsibilities:
- Starts a new logging session.
- Generates timestamps and session IDs.
- Records executed commands.
- Records suspicious activities and detected signals.
- Ends the logging session.

The log entries use a structured format:

timestamp|session_id|event|details

The log file is stored in the logs directory.

## 5. Security Module – security.c and security.h

The security module detects potentially suspicious commands using predefined rules.

Responsibilities:
- Checks commands against suspicious patterns.
- Identifies potentially dangerous command categories.
- Generates security alerts.
- Prevents detected suspicious commands from being processed by the simulated shell.

Examples of monitored patterns include sudo, rm -rf, chmod, passwd, /etc/shadow, and chown.

This module uses rule-based detection rather than advanced threat detection.

## 6. Signal Handling Module – signals.c and signals.h

The signal handling module detects selected POSIX signals.

Signals handled:
- SIGINT – Interrupt signal.
- SIGTSTP – Terminal stop signal.
- SIGHUP – Hangup signal.

Responsibilities:
- Registers signal handlers.
- Detects incoming signals.
- Stores pending signal information.
- Allows the main program to process and log detected signals.

The signal handler uses a signal-safe flag, while logging and message display are performed by the main program.

## 7. Session Inspector – scripts/inspect.sh

The inspect.sh file is a Bash script used to analyze the session log.

Responsibilities:
- Reads recorded session logs.
- Counts total sessions and commands.
- Identifies suspicious activities.
- Summarizes signal events.
- Displays session information.
- Generates a session analysis report.

The generated report is stored in reports/session_report.txt.

## 8. Build System – Makefile

The Makefile automates compilation and execution.

Available targets:

- make – Compiles the project.
- make run – Builds and runs the application.
- make inspect – Runs the session inspection script.
- make clean – Removes the compiled executable.

## 9. Conclusion

The modular design of IntruderFound makes the project easier to understand, maintain, and extend. Each module performs a specific task, while the main module coordinates the complete application.

