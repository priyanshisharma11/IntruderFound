# INTRUDERFOUND – VERIFIED TEST SUITE

All test cases are verified against the updated codebase.

| # | Test Area | Input Command | Expected Response / Behavior | Result |
| :---: | :--- | :--- | :--- | :---: |
| **1** | System Identity | `whoami`, `id`, `uname -a` | Displays `user123`, UID/GID 1001, and simulated Linux kernel string | **PASSED** |
| **2** | Working Directory | `pwd` | Displays `/home/user123` | **PASSED** |
| **3** | Inode & Permissions Listing | `ls -la` | Displays POSIX long format with permissions (`drwxr-xr-x`, `-rw-r--r--`), size, and date | **PASSED** |
| **4** | Directory Creation & Traversal | `mkdir test_dir && cd test_dir` | Creates directory, updates prompt to `user123@srv-node01:/home/user123/test_dir$ ` | **PASSED** |
| **5** | Path Resolution (`..`, `/`, `~`) | `cd ..`, `cd ~`, `cd /home/user123` | Correctly resolves relative and absolute paths | **PASSED** |
| **6** | File Redirection & Inode Writing | `echo "first line" > hello.txt` | Creates file node, assigns inode, writes content | **PASSED** |
| **7** | File Redirection Appending | `echo "second line" >> hello.txt` | Appends newline and text without buffer overflow | **PASSED** |
| **8** | Path-Aware File Reading | `cat hello.txt` | Outputs file contents accurately | **PASSED** |
| **9** | File Copy & Removal | `cp hello.txt copy.txt && rm copy.txt` | Copies file content to destination inode and removes node cleanly | **PASSED** |
| **10** | Modal VI Editor Trap | `vi secrets.txt` | Opens raw-mode modal editor (`i`, real `ESC`, `:wq`, `~` empty lines) | **PASSED** |
| **11** | False-Positive Immunity | `echo "pseudo code works"`, `cat notes.txt` | Innocent commands containing substrings are not flagged | **PASSED** |
| **12** | Privilege Escalation Deception | `sudo apt update`, `su -` | Prompts for password, rejects auth as failed password attempts without revealing honeypot identity | **PASSED** |
| **13** | File Permission Deception | `chmod 777 secrets.txt`, `chown root secrets.txt` | Rejects with authentic `Operation not permitted`, logs alert silently | **PASSED** |
| **14** | Destructive Command Deception | `rm -rf /` | Rejects with authentic safety error, logs threat silently | **PASSED** |
| **15** | Sensitive System File Deception | `cat /etc/shadow` | Rejects with authentic `Permission denied`, logs threat silently | **PASSED** |
| **16** | POSIX Signal Interception | `Ctrl+C` (SIGINT), `Ctrl+Z` (SIGTSTP) | Shell intercepts signals, preserves REPL, prints `^C`, logs event silently | **PASSED** |
| **17** | POSIX File Descriptor Logging | `logger_log()` | Uses `open(..., O_APPEND)`, `write()`, and `fsync()` system calls | **PASSED** |
| **18** | Forensic Analytics Pipeline | `make inspect` | Shell pipeline (grep, sed, awk, trap) computes duration and writes Markdown & Text reports | **PASSED** |
