# IntruderFound: Interactive Command-Line Honeypot & Attacker Session Inspector

## 1. Project Overview

IntruderFound is an educational command-line honeypot simulation developed using C programming and UNIX/Linux concepts.

It provides a simulated POSIX-like terminal environment where users can interact with a virtual file system and execute supported commands. The system monitors user activity, identifies suspicious commands, records session events, and generates an analysis report.

The project demonstrates basic honeypot concepts, command monitoring, signal handling, file system simulation, and shell scripting.

## 2. Objectives

- Develop an interactive simulated command-line environment.
- Implement a virtual file system.
- Detect and block selected suspicious commands.
- Maintain logs of user activities and sessions.
- Handle UNIX signals such as SIGINT, SIGTSTP, and SIGHUP.
- Analyze session logs using a Bash script.
- Generate reports containing suspicious activities and command statistics.

## 3. Features

### Interactive Decoy Shell
Provides a simulated terminal with commands such as:
- help
- pwd
- ls
- cd
- whoami
- mkdir
- touch
- cat
- echo
- vi
- exit

### Virtual File System
Maintains simulated directories and files, allowing users to navigate directories, create files, read content, and perform basic file operations.

### Simulated VI Editor
Provides a simple editor interface for modifying virtual file contents.

### Suspicious Command Detection
Identifies selected suspicious commands and blocks their execution. Examples include:
- sudo
- rm -rf
- chmod
- passwd
- chown
- Access to sensitive system files such as /etc/shadow

### Session Logging
Records commands, suspicious activities, and signal events with timestamps and session identifiers.

### Signal Handling
Handles the following UNIX signals:
- SIGINT
- SIGTSTP
- SIGHUP

### Bash Session Inspector
Analyzes session logs and generates a report containing:
- Total sessions
- Total commands
- Suspicious activities
- Signal events
- Command frequency
- Session start and end times

## 4. Technologies Used

- Programming Language: C
- Scripting Language: Bash
- Operating System: Ubuntu Linux
- Compiler: GCC
- Build Tool: GNU Make
- Version Control: Git and GitHub

## 5. Project Structure

```text
IntruderFound/
│
├── src/
│   ├── main.c
│   ├── editor.c
│   ├── editor.h
│   ├── logger.c
│   ├── logger.h
│   ├── security.c
│   ├── security.h
│   ├── signals.c
│   └── signals.h
│
├── scripts/
│   └── inspect.sh
│
├── logs/
│   └── session.log
│
├── reports/
│   └── session_report.txt
│
├── tests/
│   └── test_cases.md
│
├── docs/
├── integration.txt
├── Makefile
└── README.md
```

## 6. Installation and Execution

### Step 1: Clone the repository

```bash
git clone <your-github-repository-link>
```

### Step 2: Enter the project directory

```bash
cd IntruderFound
```

### Step 3: Compile the project

```bash
make
```

### Step 4: Run IntruderFound

```bash
make run
```

### Step 5: Analyze session activity

After using the simulated shell, exit the session and run:

```bash
make inspect
```

The session analysis report will be generated at:

```text
reports/session_report.txt
```

### Step 6: Clean the compiled executable

```bash
make clean
```

## 7. Sample Execution

```text
====================================
       INTRUDFOUND DECOY SHELL
====================================
Welcome, intruder!
Type help to see available commands.

intruder@decoy:~$ whoami
intruder

intruder@decoy:~$ sudo apt install something

[SECURITY ALERT] Suspicious command detected!
Category: Privilege escalation attempt
Command blocked by IntruderFound.

intruder@decoy:~$ exit
Session ended.
```

## 8. Expected Session Report

The session inspector generates a report containing:

- Total sessions
- Total commands
- Number of suspicious activities
- Number of signal events
- Suspicious activity details
- Command frequency
- Session details

## 9. Security and Limitations

IntruderFound is an educational honeypot simulation and not a production security system.

- Commands operate within a simulated environment.
- Suspicious command detection uses predefined rules.
- The virtual file system does not modify the actual system file structure.
- The project does not provide real-world intrusion prevention or complete threat detection.

## 10. Conclusion

IntruderFound demonstrates how a simulated honeypot can monitor command-line activity, identify selected suspicious operations, maintain session logs, handle UNIX signals, and generate useful activity reports.

The project combines C programming, UNIX/Linux concepts, Bash scripting, and file handling to provide a practical learning experience in basic system security monitoring.
