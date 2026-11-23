# INTRUDERFOUND – MODULE DOCUMENTATION

## 1. Introduction

IntruderFound is an interactive command-line honeypot simulation developed using C programming (POSIX/C11) and UNIX shell automation pipelines. It provides an authentic simulated POSIX terminal environment designed to trap unauthorized users, log telemetry silently, handle UNIX signals gracefully, simulate an in-memory virtual filesystem with inode metadata, and generate automated forensic analytics reports.

## 2. Main Architecture & Virtual File System – `main.c`

The main engine orchestrates the Read-Eval-Print Loop (REPL), signal checking, path resolution, and command dispatch.

### In-Memory Virtual File System (VFS) with Inodes
- **Inode Abstraction (`struct Inode`)**: Each virtual file and directory is represented by a simulated inode containing:
  - `ino`: Unique inode identifier.
  - `is_directory`: Directory vs regular file flag.
  - `mode`: POSIX file permission bits (`mode_t`, e.g., `0755`, `0644`, `0600`).
  - `owner` & `group`: Ownership attributes (e.g. `user123`, `root`).
  - `size`: File size in bytes.
  - `mtime`: Last modification timestamp.
  - `content`: Buffer storing in-memory file data.
- **Directory Hierarchy (`struct Node`)**: Links directory entries to their underlying inodes, supporting multi-level n-ary tree traversal.
- **Path Resolution (`resolve_path`)**: Resolves multi-level relative and absolute paths, handling `/`, `~`, `.` (current directory), and `..` (parent directory).
- **Supported Built-in Utilities**:
  - `ls [-l|-la] [path]`: Supports both short and full POSIX formatted long listing (permissions, owner, group, size, date).
  - `cd [path]`: Multi-level directory navigation.
  - `pwd`: Absolute path calculation from the virtual root.
  - `cat [path]`: Path-aware file reading.
  - `echo [text] [> | >> [path]]`: In-memory redirection and appending with buffer safety.
  - `touch [path]`: Creates files or updates inode modification times.
  - `mkdir [path]`: Creates virtual directories with `0755` permissions.
  - `rm [path]`: Removes virtual files.
  - `cp [src] [dst]`: Copies files across directories.
  - `mv [src] [dst]`: Moves or renames files.
  - `whoami`, `id`, `uname [-a]`: System and identity emulation.
  - `exit`: Clean session termination.

## 3. Simulated VI Text Editor – `editor.c` & `editor.h`

Implements a modal text editor trap mimicking native `vi`/`vim`:
- **Terminal Raw Mode (`termios.h`)**: Puts terminal into raw mode (`ICANON` and `ECHO` disabled) when connected to an interactive TTY.
- **Real Modal Editing**:
  - **NORMAL Mode**: Default mode; supports navigation, `i` to enter INSERT mode, and `:` to enter EX command mode.
  - **INSERT Mode**: Interactive typing and character buffer insertion; backspace deletion.
  - **Escape Key Handling**: Intercepts the actual ASCII Escape byte (`0x1B` / 27) to return to NORMAL mode.
  - **EX Commands**: `:w` (save to inode), `:q` (quit), `:wq` (save and quit), `:q!` (quit without saving).
- **Visual Interface**: Emits ANSI escape sequences to clear the screen, renders empty line tildes (`~`), and displays status indicators (`-- INSERT --`, status messages).
- **Non-Interactive Fallback**: Fallback mode for headless automated test pipelines.

## 4. Low-Level Audit Logger – `logger.c` & `logger.h`

Implements append-only session telemetry using low-level POSIX system calls:
- **POSIX System Calls**: Uses `open(..., O_WRONLY | O_CREAT | O_APPEND, 0644)`, `write()`, and `close()`.
- **Durability**: Employs `fsync()` after each write to ensure disk persistence.
- **Session Identification**: Unique session IDs constructed via `YYYYMMDD_HHMMSS_PID`.
- **Telemetry Format**: `timestamp|session_id|event|details`.
- **Sanitization**: Filters delimiter (`|`) and newline injection attacks.

## 5. Security & Honeypot Deception Engine – `security.c` & `security.h`

Implements threat classification and authentic deception:
- **Tokenized Parsing**: Parses command tokens cleanly, eliminating false positives on substring matches (e.g. `echo pseudo` or `cat notes.txt` are permitted without false alarms).
- **Deception Without Revealing the Honeypot**: Rather than displaying warning banners that give away the honeypot, the engine silently logs the malicious event and returns genuine UNIX error messages:
  - `sudo`: Prompts for a password without echo (`[sudo] password for user123:`) and rejects with an authentic auth failure (`sudo: 3 incorrect password attempts`).
  - `su`: Prompts for password and reports `su: Authentication failure`.
  - `chmod`: Returns `chmod: changing permissions of '...': Operation not permitted`.
  - `chown` / `chgrp`: Returns `...: changing ownership of '...': Operation not permitted`.
  - `passwd`: Simulates password prompt and fails with `passwd: Authentication token manipulation error`.
  - `rm -rf /`: Simulates safety guard `rm: it is dangerous to operate recursively on '/'`.
  - Sensitive files (`/etc/shadow`, `/etc/sudoers`, `/root`): Returns `Permission denied`.
  - Package tools (`apt`, `yum`): Returns authentic lock failure (`Could not open lock file... are you root?`).

## 6. Signal Interception Module – `signals.c` & `signals.h`

Uses POSIX `sigaction` to intercept terminal interrupt signals:
- **SIGINT (Ctrl+C)**: Intercepted; prevents shell termination, logs event, and prints `^C` with a fresh prompt.
- **SIGTSTP (Ctrl+Z)**: Intercepted; prevents process suspension, logs event, and preserves terminal state.
- **SIGHUP (Hangup)**: Intercepted; logs session termination and closes file descriptors gracefully.

## 7. Forensic Session Inspector Pipeline – `scripts/inspect.sh`

Automated log analytics engine adhering to the UNIX philosophy:
- **POSIX Signal Traps**: Uses `trap 'rm -f ...' EXIT INT TERM` for temporary file hygiene.
- **Grep Filter**: Extracts and sanitizes valid telemetry entries.
- **Sed Preprocessor**: Normalizes whitespace and fields.
- **Awk Analytics**: Aggregates command frequency distributions, flags security events, and summarizes metrics.
- **Session Duration Calculation**: Computes exact elapsed session times (`Xm Ys`) using POSIX date translation.
- **Multi-Format Export**: Generates both plain text (`reports/session_report.txt`) and formatted GitHub Flavored Markdown (`reports/session_report.md`).
