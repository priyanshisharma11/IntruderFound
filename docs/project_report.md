# Jaypee Institute of Information Technology
## Sector-62, Noida
### Department of Computer Science and Engineering and Information Technology

---

# Project Report
## On
# IntruderFound – Interactive Command-Line Honeypot & Attacker Session Inspector

**UNIX PROGRAMMING LAB**  
**Course Code:** 24B15CS214  
**Session:** Odd Semester (2026-2027)  
**Program:** B. Tech. CSE, Second Year 3rd Semester  

**Submitted by:**  
* Priyanshi Sharma (2501030218)  
* Shourya Somani (2501030221)  
* Navneet Patel (2501030227)  
* Riddhi Jaggi (2501030232)  
* Dhruv Mittal (2501030233)  
**Batch:** B5  

**Submitted to:**  
* Mr. Baibhav Singh  

---

## Table of Contents

* **Chapter 1: Introduction**
  * 1.1 Background
  * 1.2 Problem Statement
  * 1.3 Social & Environmental Relevance (SDGs)
  * 1.4 Scope and Requirements
* **Chapter 2: System Design & Methodology**
  * 2.1 Proposed Methodology and Architecture Flow
  * 2.2 Tool and Technique Selection
  * 2.3 Implementation of Object-Oriented Concepts in C
* **Chapter 3: Implementation & Testing**
  * 3.1 Experimental Setup
  * 3.2 Results and Verification Matrix
  * 3.3 Verified Interactive Terminal Output
* **Chapter 4: Conclusion & Future Scope**
  * 4.1 Summary of Work and Achievements
  * 4.2 Societal Impact, Sustainability, and Ethical Compliance
  * 4.3 Limitations and Future Scope
* **References**
* **Appendix: Team Roles and Contributions**

---

## Chapter 1: Introduction

### 1.1 Background
Command-line interfaces (CLIs) are the primary mechanism used to administer Linux and UNIX-like systems. A terminal provides direct, privileged access to utilities for navigating directory trees, inspecting file contents, modifying permissions, managing user accounts, and invoking system binaries. This flexibility is essential for system administration, but it also means that unauthorized commands executed by an adversary can lead to rapid compromise or destruction of critical host data. In a security-learning and threat-intelligence context, it is valuable to observe how an unauthorized user or automated bot explores an environment without exposing genuine host operating systems or production data to potentially destructive operations.

A honeypot is an active decoy system designed to lure, detect, and record unauthorized interactions. Rather than simply blocking access at the firewall level, a honeypot traps the intruder inside a controlled, observable perimeter. IntruderFound applies this paradigm directly to the UNIX command-line environment. Developed in C with a post-session analytics engine in POSIX shell scripting, IntruderFound presents a realistic POSIX terminal environment (`user123@srv-node01:~$ `) that emulates an authentic Linux system, intercepts terminal signals, contains file manipulations inside an in-memory Virtual File System, and silently logs telemetry for automated analysis.

### 1.2 Problem Statement
Demonstrating and studying suspicious terminal behavior on a real operating system poses severe operational risks. Destructive commands (e.g., `rm -rf /`), privilege escalation workflows (`sudo`, `su`), or unauthorized access to sensitive locations (`/etc/shadow`) cannot be safely executed on a live production or laboratory host. Furthermore, native shell history mechanisms (`.bash_history`) are easily erased, tampered with, or bypassed by an intruder. Conventional educational demonstrations frequently suffer from three primary shortcomings:
1. **Lack of Sandbox Isolation:** Running actual system shells allows genuine host modifications, risking malware persistence or accidental host deletion.
2. **The Honeypot Paradox:** Naive simulators often display overt security warning banners (e.g., `[SECURITY ALERT] Command blocked by IntruderFound`), instantly revealing the decoy to the attacker and breaking the psychological containment necessary for observation.
3. **Inadequate Forensic Automation:** Raw terminal logs are cumbersome to analyze manually without an automated pipeline to extract metrics, identify command distributions, and compute session timelines.

IntruderFound addresses these problems by providing an in-memory, sandboxed terminal decoy that mimics authentic Linux behavior, handles interrupts gracefully, responds to malicious attempts with genuine operating-system error messages, and automatically compiles structured incident reports.

### 1.3 Social & Environmental Relevance
Cybersecurity attacks against public digital infrastructure, academic institutions, and enterprise networks cause billions of dollars in operational damage annually. By providing an open-source, resource-efficient decoy terminal, IntruderFound democratizes early-warning threat detection without requiring expensive proprietary hardware or multi-node hypervisor infrastructure. Environmentally, running a lightweight in-memory C simulation consumes negligible CPU cycles and memory compared to heavy virtual machines, substantially reducing the carbon footprint of continuous security monitoring.

* **Primary Sustainable Development Goals (SDGs):**
  * **SDG 9 (Industry, Innovation and Infrastructure):** Promotes resilient technological infrastructure, secure computing environments, and proactive defense against unauthorized digital intrusion.
  * **SDG 16 (Peace, Justice and Strong Institutions):** Strengthens institutional defense capabilities and transparency against cybercrime through immutable forensic logging and accountability.
* **Secondary Sustainable Development Goals (SDGs):**
  * **SDG 4 (Quality Education):** Serves as an educational framework for teaching low-level POSIX concepts, signal processing, and defensive systems engineering.

### 1.4 Scope and Requirements
IntruderFound is architected as an educational, local command-line honeypot simulation. It encompasses:
* **Decoy Shell REPL:** An interactive decoy shell loop presenting an authentic non-root user prompt (`user123@srv-node01:~$ `).
* **VFS & Inodes:** An in-memory Virtual File System (VFS) with `struct Inode` and `struct Node`, supporting permissions (`mode_t`), timestamps, ownership, and multi-level path resolution (`cd`, `ls -la`, `pwd`, `mkdir`, `touch`, `cat`, `rm`, `cp`, `mv`).
* **Stream Redirection:** In-memory stream redirection (`>` and `>>`) with rigorous buffer-overflow checks.
* **Modal VI Editor Trap:** A modal text editor using `termios` raw mode, capturing the physical Escape key (`0x1B`), and handling `:w`, `:q`, `:wq`, and `:q!`.
* **POSIX Signal Interception:** Asynchronous signal interception (`SIGINT`, `SIGTSTP`, `SIGHUP`) via POSIX `sigaction`, reissuing fresh prompts without terminating.
* **Honeypot Deception Engine:** Context-aware command tokenization that simulates authentic Linux errors (`sudo: 3 incorrect password attempts`, `Permission denied`) rather than warning the adversary.
* **Append-Only Audit Logger:** Low-level POSIX system call logging (`open`, `write`, `fsync`) with binary path resolution for guaranteed log persistence.
* **Forensic Analytics Suite:** A pipelined analytics utility combining `grep`, `sed`, and `awk` with POSIX traps to compute session durations and generate Markdown and text incident reports.

---

## Chapter 2: System Design & Methodology

### 2.1 Proposed Methodology and Architecture Flow
IntruderFound is organized around two cooperating subsystems: the Decoy Shell Engine (front-end interactive C program) and the Forensic Session Inspector (back-end shell automation pipeline).

User keystrokes enter the REPL in `main.c`. The signal shield (`signals.c`) intercepts terminal interrupts. The security detector (`security.c`) inspects tokenized command verbs: recognized threats trigger authentic simulated Linux errors. Safe commands operate upon the in-memory tree hierarchy. Simultaneously, all events are piped to the append-only log via `logger.c`. Finally, `inspect.sh` parses the log file offline to produce comprehensive forensic incident reports.

*Figure 1: IntruderFound processing flow, from user input through signal interception, deception checks, and VFS execution, to post-session forensic inspection.*

### 2.2 Tool and Technique Selection
The development stack was selected based on systems-level control, standards compliance, and execution efficiency:
* **C Programming Language (C11 / POSIX.1-2008):** Chosen for unmanaged memory control, low-level POSIX system calls, terminal `termios` configuration, and minimal CPU footprint.
* **GCC Toolchain & GNU Make:** Provides strict compiler diagnostics (`-Wall -Wextra -std=c11`) and reproducible automated builds across Linux and macOS.
* **POSIX Shell Scripting (Bash, awk, sed, grep):** Implements the UNIX philosophy of pipelining modular text-stream processors (`grep` for filtering, `sed` for normalization, and `awk` for associative array calculations).

### 2.3 Implementation of Object-Oriented Concepts in C
Although compiled procedurally, IntruderFound is structured around core Object-Oriented Programming (OOP) paradigms to ensure clean abstraction, encapsulation, and maintainability:
1. **Encapsulation & Information Hiding:** Internal subsystem states—including the log file descriptor (`log_fd`), session identifier (`session_id`), original terminal settings (`orig_termios`), and signal state (`pending_signal`)—are declared with `static` file scope in their respective `.c` units. They cannot be accessed or altered directly by external modules, enforcing private member encapsulation through public header declarations.
2. **Object Modeling via Struct Composition:** The virtual file system models real-world UNIX files and directories through object composition. An `Inode` struct encapsulates metadata (permissions, owner, group, size, `mtime`, and data buffer), while a `Node` struct models the directory tree entry. This separation directly mirrors entity-component object modeling.
3. **Constructors and Destructors (ADTs):** Creation of inodes and directory nodes is mediated by factory functions (`create_inode()`, `create_node()`), acting as parameterized constructors that ensure valid state initialization. Systematic tree deallocation routines act as object destructors.
4. **Polymorphic Behavior:** Node traversal functions inspect `node->inode->is_directory` at runtime, dynamically branching between directory stream listing (`list_directory`) and file buffer reading (`cat` / `open_editor`), demonstrating runtime polymorphic dispatch.

---

## Chapter 3: Implementation & Testing

### 3.1 Experimental Setup
The system was compiled and evaluated in a standard POSIX UNIX environment:
* **Host Environments:** macOS Darwin (Apple Silicon, ARM64) and Ubuntu Linux 22.04 LTS (x86_64).
* **Compiler Toolchain:** Apple clang 15.0+ / GNU GCC 11.4+.
* **Build Automation:** GNU Make 3.81 (macOS native) and GNU Make 4.3 (Linux).
* **Terminal Interface:** xterm-256color compliant terminal emulator with `termios` raw-mode support.
* **Compiler Flags:** `-Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE`

### 3.2 Results and Verification Matrix
The application was subjected to functional verification covering identity emulation, VFS manipulation, stream redirection, vi modal editing, deception logic, signal handling, low-level logging, and forensic report generation.

| Test ID | Module Under Test | Input Command / Action | Expected Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | Identity | `whoami`, `id`, `uname -a` | Emulates user123 (UID 1001) on srv-node01 | **PASS** |
| **TC-02** | Path Navigation | `cd Documents && pwd` | Resolves path to /home/user123/Documents | **PASS** |
| **TC-03** | VFS Metadata | `ls -la` | Displays POSIX listing with drwxr-xr-x & sizes | **PASS** |
| **TC-04** | Redirection | `echo 'secret' > key.txt` | Creates inode, writes buffer, readable via cat | **PASS** |
| **TC-05** | Appending | `echo 'extra' >> key.txt` | Appends newline and content safely without overflow | **PASS** |
| **TC-06** | File Operations | `cp key.txt copy.txt && rm copy.txt` | Duplicates inode content; removes file cleanly | **PASS** |
| **TC-07** | VI Editor Trap | `vi secrets.txt` | Raw terminal mode; real Esc key; saves on :wq | **PASS** |
| **TC-08** | Privilege Deception | `sudo su` | Prompts for password; returns authentic 3 failed attempts | **PASS** |
| **TC-09** | Destructive Check | `rm -rf /` | Emits dangerous operation warning; zero honeypot leak | **PASS** |
| **TC-10** | Sensitive Files | `cat /etc/shadow` | Returns authentic 'Permission denied' | **PASS** |
| **TC-11** | False Positive | `echo 'pseudo code'` | Allows innocent commands containing 'sudo' substring | **PASS** |
| **TC-12** | Signal Interception | `Ctrl+C` (SIGINT) | Intercepts signal; prints ^C; reissues prompt cleanly | **PASS** |
| **TC-13** | POSIX Logger | Runtime activity | Writes via open, write, fsync with path resolution | **PASS** |
| **TC-14** | Analytics Suite | `make inspect` | Parses logs; calculates exact duration; writes MD/TXT | **PASS** |

*Table 1: Functional verification matrix of IntruderFound.*

### 3.3 Verified Interactive Terminal Output
```text
user123@srv-node01:~$ whoami
user123

user123@srv-node01:~$ id
uid=1001(user123) gid=1001(user123) groups=1001(user123)

user123@srv-node01:~$ pwd
/home/user123

user123@srv-node01:~$ ls -la
total 9
drwxr-xr-x 1 user123  user123    4096 Nov 23 00:33 Documents/
drwxr-xr-x 1 user123  user123    4096 Nov 23 00:33 Downloads/
-rw------- 1 user123  user123      47 Nov 23 00:33 secrets.txt

user123@srv-node01:~$ sudo su
[sudo] password for user123: 
sudo: 3 incorrect password attempts

user123@srv-node01:~$ cat /etc/shadow
cat: /etc/shadow: Permission denied

user123@srv-node01:~$ rm -rf /
rm: it is dangerous to operate recursively on '/'
rm: use --no-preserve-root to override this failsafe

user123@srv-node01:~$ exit
logout
```

---

## Chapter 4: Conclusion & Future Scope

### 4.1 Summary of Work and Achievements
IntruderFound demonstrates a successful integration of UNIX systems programming, low-level C memory management, and defensive cybersecurity engineering. The project achieves:
* **Believable Decoy Shell:** A convincing Linux terminal prompt that actively maintains the deception of a live machine.
* **Virtual Inode File System:** In-memory structs simulating inodes, permissions, timestamps, and multi-level path traversal.
* **Interactive vi Trap:** A modal editor trap capturing real Escape keys using `termios` raw mode.
* **Process & Signal Resilience:** POSIX `sigaction` handlers that prevent termination on `SIGINT`, `SIGTSTP`, and `SIGHUP`.
* **Kernel-Level I/O Logging:** Append-only logging via `open()`, `write()`, and `fsync()` system calls with binary path auto-resolution.
* **Automated Forensic Analytics:** A shell pipeline combining `grep`, `sed`, and `awk` that computes exact session durations and produces Markdown and text reports.

Applying Object-Oriented Programming (OOP) concepts in C—specifically through structural encapsulation, data hiding, and polymorphic node processing—enabled robust modular isolation and seamless collaboration across all five team members.

### 4.2 Societal Impact, Sustainability, and Ethical Compliance
From an institutional perspective, IntruderFound equips system administrators with vital post-exploitation telemetry, revealing attacker priorities without endangering production assets. From an environmental perspective, running in-memory C simulations eliminates the energy and computational overhead of multi-gigabyte virtual machines, lowering monitoring power requirements. Ethically, IntruderFound is purely defensive: it operates strictly within an isolated local sandbox, refraining from active counter-attacks, port scanning, or external offensive payloads.

### 4.3 Limitations and Future Scope
* **In-Memory Volatility:** The virtual file system resides in volatile memory and resets upon process exit.
* **Pipeline Emulation:** I/O redirection currently supports file overwrite (`>`) and append (`>>`), but does not yet emulate inter-process pipes (`|`).

**Future Enhancements:**
1. Binding the decoy engine to a lightweight pseudo-SSH daemon using `libssh` on port 2222 to capture remote botnet attacks over the network.
2. Serializing in-memory inode states to an encrypted SQLite file so that the virtual environment persists across sessions.
3. Streaming parsed JSON forensic logs directly to enterprise SIEM platforms (Splunk, ElasticSearch).

---

## References

[1] W. R. Stevens and S. A. Rago, *Advanced Programming in the UNIX Environment*, 3rd ed. Boston, MA: Addison-Wesley, 2013.  
[2] M. Kerrisk, *The Linux Programming Interface: A Linux and UNIX System Programming Handbook*. San Francisco, CA: No Starch Press, 2010.  
[3] L. Spitzner, *Honeypots: Tracking Hackers*. Boston, MA: Addison-Wesley, 2003.  
[4] IEEE Computer Society, *Standard for Information Technology—Portable Operating System Interface (POSIX®) Base Specifications, Issue 7*, IEEE Std 1003.1-2008, 2018.  
[5] D. Dougherty and A. Robbins, *sed & awk*, 2nd ed. Sebastopol, CA: O'Reilly Media, 1997.  

---

## Appendix: Team Roles and Contributions

* **Dhruv Mittal (2501030233) — Lead Architecture & Standard I/O Engineer:**  
  Architected the primary interactive Read-Eval-Print Loop (REPL) in C. Configured GNU Make and GCC build automation with strict POSIX compliance flags. Managed standard I/O buffer flushing (`fflush`) and terminal prompt authenticity. Coordinated system-level module integration.
* **Riddhi Jaggi (2501030232) — Virtual File System & Inode Architect:**  
  Designed the in-memory virtual directory hierarchy using C structs (`Inode` and `Node` abstractions). Implemented POSIX file permission modeling (`mode_t`), timestamps, and ownership attributes. Developed multi-level recursive path resolution (`resolve_path`) and POSIX formatted directory listing (`ls -la`).
* **Shourya Somani (2501030221) — Editor Trap & Command Dispatcher:**  
  Engineered the simulated modal `vi` editor trap utilizing `termios` raw mode and escape sequence handling. Implemented command dispatch routines for file manipulation (`touch`, `cat`, `rm`, `cp`, `mv`). Developed safe in-memory stream redirection (`>` and `>>`) with buffer overflow protection.
* **Navneet Patel (2501030227) — POSIX System Calls & Signal Security Lead:**  
  Implemented signal interception routines using POSIX `sigaction` for `SIGINT`, `SIGTSTP`, and `SIGHUP`. Developed the append-only audit logging engine using low-level POSIX file descriptors (`open`, `write`, `fsync`). Engineered dynamic executable path self-resolution (`_NSGetExecutablePath` / `/proc/self/exe`) for persistent logging.
* **Priyanshi Sharma (2501030218) — Telemetry Analyst & Shell Automation Engineer:**  
  Engineered the backend automated forensic analytics pipeline (`scripts/inspect.sh`). Chained `grep`, `sed`, and `awk` filters to extract telemetry metrics and calculate command frequency distributions. Implemented portable epoch timestamp math for session duration tracking and automated Markdown and plain text report generation.
