INTRUDFOUND - TEST CASES

1. BASIC SHELL
   Input: help
   Expected: Display available commands
   Result: To be verified

2. USER IDENTIFICATION
   Input: whoami
   Expected: Display intruder
   Result: To be verified

3. DIRECTORY NAVIGATION
   Input: cd Documents
   Expected: Change virtual directory
   Result: To be verified

4. FILE CREATION
   Input: touch test.txt
   Expected: Create virtual file
   Result: To be verified

5. FILE WRITING
   Input: echo Hello > test.txt
   Expected: Write content into virtual file
   Result: To be verified

6. FILE APPENDING
   Input: echo World >> test.txt
   Expected: Append content to virtual file
   Result: To be verified

7. FILE READING
   Input: cat test.txt
   Expected: Display virtual file content
   Result: To be verified

8. VI EDITOR
   Input: vi test.txt
   Expected: Open simulated editor
   Result: To be verified

9. SUSPICIOUS COMMAND
   Input: rm -rf Documents
   Expected: Detect and block command
   Result: To be verified

10. SESSION LOGGING
    Input: Execute several commands
    Expected: Record commands with timestamps
    Result: To be verified

11. SIGNAL HANDLING
    Input: Ctrl+C and Ctrl+Z
    Expected: Detect signals without terminating
    Result: To be verified

12. BASH SESSION INSPECTOR
    Input: ./scripts/inspect.sh
    Expected: Generate session analysis report
    Result: To be verified

