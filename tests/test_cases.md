# INTRUDERFOUND – TEST CASES

## 1. Basic Shell
- Input: `help`
- Expected: Display available commands.
- Result: PASSED

## 2. User Identification
- Input: `whoami`
- Expected: Display `intruder`.
- Result: PASSED

## 3. Directory Navigation
- Input: `cd Documents`
- Expected: Change the virtual directory.
- Result: PASSED

## 4. File Creation
- Input: `touch test.txt`
- Expected: Create a virtual file.
- Result: PASSED

## 5. File Writing
- Input: `echo Hello > test.txt`
- Expected: Write content into the virtual file.
- Result: PASSED

## 6. File Appending
- Input: `echo World >> test.txt`
- Expected: Append content to the virtual file.
- Result: PASSED

## 7. File Reading
- Input: `cat test.txt`
- Expected: Display virtual file content.
- Result: PASSED

## 8. Simulated VI Editor
- Input: `vi test.txt`
- Expected: Open, edit, save, and exit the simulated editor.
- Result: PASSED

## 9. Suspicious Command Detection
- Input: `sudo apt install something`
- Expected: Detect and block the suspicious command.
- Result: PASSED

## 10. Session Logging
- Input: Execute commands inside the decoy shell.
- Expected: Record commands with timestamps and session IDs.
- Result: PASSED

## 11. Signal Handling
- Input: Ctrl+C and Ctrl+Z.
- Expected: Detect signals without terminating or suspending the decoy shell.
- Result: PASSED

## 12. Bash Session Inspector
- Input: `make inspect`
- Expected: Generate a session analysis report.
- Result: PASSED

## Conclusion

All 12 test cases have been verified successfully. IntruderFound demonstrates interactive shell operation, virtual file management, simulated text editing, suspicious command detection, session logging, signal handling, and automated session report generation.

