import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_page_number(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_report():
    doc = Document()

    # Section & Page Setup (A4, 2cm margins)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    # Footer setup for page numbering
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.add_run()
    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(10)
    footer_run.font.color.rgb = RGBColor(128, 128, 128)
    add_page_number(footer_run)

    # Configure Default Style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(30, 30, 30)

    # Helper: Title Paragraph
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(16)
        run.font.bold = True
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(60, 60, 60)
        return p

    def add_chapter_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 32, 96) # Dark Navy
        return p

    def add_subheading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_subsubheading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.font.bold = True
        return p

    def add_body_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.5
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Times New Roman"
            r_pre.font.size = Pt(12)
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.3
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Times New Roman"
            r_pre.font.size = Pt(12)
            r_pre.font.bold = True
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        return p

    def add_code_block(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F4F5F7")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(code_text)
        run.font.name = "Courier New"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(20, 20, 20)
        # Empty space after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # TITLE PAGE
    # -------------------------------------------------------------
    add_title("Jaypee Institute of Information Technology, Noida")
    add_subtitle("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING AND INFORMATION TECHNOLOGY")

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(6)
    p_proj.paragraph_format.space_after = Pt(12)
    r_proj = p_proj.add_run("Project Title:\nIntruderFound: Interactive Command-Line Honeypot & Attacker Session Inspector")
    r_proj.font.name = "Times New Roman"
    r_proj.font.size = Pt(15)
    r_proj.font.bold = True
    r_proj.font.color.rgb = RGBColor(0, 32, 96)

    # JIIT Logo
    if os.path.exists("/tmp/jiit_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture("/tmp/jiit_logo.png", width=Inches(1.8))

    # Team Box
    table_team = doc.add_table(rows=6, cols=3)
    table_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_team, "B0C4DE")

    headers = ["Name", "Enrolment No.", "Assigned Role"]
    for j, h in enumerate(headers):
        cell = table_team.cell(0, j)
        set_cell_background(cell, "002060")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    team_data = [
        ("Dhruv Mittal", "[Enrolment No. 1]", "Lead Architecture & Standard I/O"),
        ("Riddhi Jaggi", "[Enrolment No. 2]", "Virtual File System & Inode Architect"),
        ("Shourya Somani", "[Enrolment No. 3]", "Editor Trap & Command Dispatcher"),
        ("Navneet Patel", "[Enrolment No. 4]", "POSIX Syscalls & Signal Security Lead"),
        ("Priyanshi Sharma", "[Enrolment No. 5]", "Telemetry Analyst & Shell Automation")
    ]

    for i, (name, enr, role) in enumerate(team_data):
        row = table_team.rows[i + 1]
        bg = "F9FAFC" if i % 2 == 0 else "FFFFFF"
        for j, val in enumerate([name, enr, role]):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            if j == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(16)
    p_meta.paragraph_format.space_after = Pt(0)
    p_meta.paragraph_format.line_spacing = 1.3
    r_meta = p_meta.add_run(
        "Course Name: Unix Programming Lab | Course Code: 24B15CS214\n"
        "Program: B. Tech. Computer Science and Engineering\n"
        "Second Year, 3rd Semester | Academic Year: 2026-2027"
    )
    r_meta.font.name = "Times New Roman"
    r_meta.font.size = Pt(11.5)
    r_meta.font.bold = True
    r_meta.font.color.rgb = RGBColor(60, 60, 60)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # -------------------------------------------------------------
    add_chapter_heading("Chapter 1: Introduction")

    add_subheading("1.1 Background")
    add_body_p(
        "In contemporary cybersecurity, systems exposed to external networks face relentless, automated reconnaissance "
        "and targeted human intrusions. Conventional defense mechanisms—such as stateful firewalls and intrusion "
        "prevention systems (IPS)—operate strictly as perimeter filters. While vital, these systems yield negligible "
        "threat intelligence regarding adversary techniques, targeted payloads, lateral movement habits, or privilege "
        "escalation attempts once perimeter barriers are breached."
    )
    add_body_p(
        "Honeypots represent an active defensive paradigm. By deploying an instrumented decoy system that convincingly "
        "mimics authentic production servers, security practitioners trap unauthorized adversaries inside an isolated, "
        "observable perimeter. In a UNIX command-line environment, a terminal honeypot provides a deceptive shell prompt, "
        "synthetic directory hierarchies, and simulated POSIX utilities. Instead of executing arbitrary code on the underlying "
        "host operating system, the honeypot intercepts all interactive user inputs, confines the adversary to an in-memory "
        "sandbox, and streams keystrokes and command telemetry to an append-only audit log for forensic inspection."
    )

    add_subheading("1.2 Problem Statement")
    add_body_p(
        "Engineering an authentic command-line honeypot poses three fundamental systems engineering challenges:"
    )
    add_bullet(
        "Directly providing an attacker with a native shell (/bin/bash) risks root breakout, host file modification, and unauthorized network traversal.",
        bold_prefix="1. The Containment Dilemma: "
    )
    add_bullet(
        "If a simulated decoy shell crashes upon receiving interrupt signals (e.g., Ctrl+C), broadcasts overt alert banners (e.g., '[SECURITY ALERT] Command blocked'), or exhibits non-standard behavior, the adversary instantly detects the deception and disengages.",
        bold_prefix="2. The Honeypot Deception Paradox: "
    )
    add_bullet(
        "Standard shell history (.bash_history) is easily purged or modified by attackers. Real-time threat analysis requires an append-only, low-level telemetry pipeline paired with automated log processing tools.",
        bold_prefix="3. The Forensic Visibility Gap: "
    )
    add_body_p(
        "IntruderFound directly addresses this gap by coupling a high-fidelity, in-memory POSIX decoy shell engine developed in C "
        "with an automated post-session forensic reporting pipeline built using UNIX shell scripting, grep, sed, and awk."
    )

    add_subheading("1.3 Social & Environmental Relevance")
    add_body_p(
        "Cyber threats against public digital infrastructure, academic institutions, and small-to-medium enterprises cause "
        "severe operational disruptions. By delivering a lightweight, open-source terminal honeypot, IntruderFound democratizes "
        "early-warning intrusion detection without requiring expensive proprietary software or high-end virtualization hardware. "
        "From an environmental perspective, running in-memory C simulations consumes negligible CPU cycles and memory compared "
        "to resource-intensive virtual machines (VMs), lowering the compute and carbon footprint associated with continuous server monitoring."
    )

    add_subsubheading("Primary Sustainable Development Goals (SDGs):")
    add_bullet("Build resilient infrastructure, promote inclusive and sustainable industrialization, and foster innovation through proactive cybersecurity tools.", bold_prefix="SDG 9 (Industry, Innovation and Infrastructure): ")
    add_bullet("Promote peaceful and inclusive societies, provide access to justice, and build effective, accountable, and transparent institutions through forensic incident accounting.", bold_prefix="SDG 16 (Peace, Justice and Strong Institutions): ")

    add_subsubheading("Secondary Sustainable Development Goals (SDGs):")
    add_bullet("Serves as an open educational framework for teaching low-level POSIX concepts, signal processing, and defensive systems engineering.", bold_prefix="SDG 4 (Quality Education): ")

    add_subheading("1.4 Scope")
    add_body_p("The operational scope of IntruderFound encompasses the following functional modules and boundaries:")
    add_bullet("Authentic REPL imitating a live Ubuntu server environment (user123@srv-node01:~$)", bold_prefix="Interactive Decoy Shell: ")
    add_bullet("In-memory directory hierarchy powered by struct Inode and struct Node, supporting permissions (mode_t), timestamps, ownership, and recursive multi-level path resolution (cd, ls -la, pwd, mkdir, touch, cat, rm, cp, mv).", bold_prefix="Virtual File System (VFS): ")
    add_bullet("Modal text editor utilizing termios raw mode, intercepting real ASCII Escape keys (0x1B), handling :w, :q, :wq, and rendering ~ lines.", bold_prefix="Modal VI Editor Trap: ")
    add_bullet("Graceful trapping of SIGINT (Ctrl+C), SIGTSTP (Ctrl+Z), and SIGHUP via sigaction, preventing process breakout while preserving terminal prompt authenticity.", bold_prefix="POSIX Signal Interception: ")
    add_bullet("Context-aware command tokenization that simulates authentic Linux errors (sudo: 3 incorrect password attempts, Permission denied) rather than warning the adversary.", bold_prefix="Honeypot Deception Engine: ")
    add_bullet("Direct POSIX system call logging (open, write, fsync) with binary path resolution for guaranteed log persistence.", bold_prefix="Append-Only Audit Logger: ")
    add_bullet("Pipelined analytics utility combining grep, sed, and awk with POSIX traps to compute session durations and generate Markdown and text incident reports.", bold_prefix="Forensic Analytics Suite: ")
    add_bullet("The virtual file system resides strictly in heap memory (volatile) to guarantee complete host isolation.", bold_prefix="Operational Boundary: ")

    # -------------------------------------------------------------
    # CHAPTER 2: SYSTEM DESIGN & METHODOLOGY
    # -------------------------------------------------------------
    add_chapter_heading("Chapter 2: System Design & Methodology")

    add_subheading("2.1 Proposed Methodology")
    add_body_p(
        "IntruderFound is architected as two tightly cooperating subsystems: the front-end Decoy Shell Engine (implemented in C) "
        "and the back-end Forensic Session Inspector (implemented in POSIX Shell Scripting). "
        "The overall execution and data flow are illustrated in Figure 2.1 below:"
    )

    # Workflow Box Diagram Table
    table_diag = doc.add_table(rows=6, cols=1)
    table_diag.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_diag, "002060")

    diag_steps = [
        ("1. Attacker Interaction & Input Ingestion", "Attacker submits command string via terminal interface; intercepted by REPL engine in main.c."),
        ("2. Asynchronous Signal Shield (signals.c)", "POSIX sigaction intercepts SIGINT (^C), SIGTSTP (^Z), SIGHUP; prevents shell termination, logs signal, reissues prompt."),
        ("3. Tokenized Threat Evaluation (security.c)", "Command line is tokenized into verbs and operands. Malicious operations (sudo, rm -rf, /etc/shadow) trigger authentic UNIX error responses."),
        ("4. In-Memory VFS & Inode Dispatch (main.c, editor.c)", "Safe commands execute against the in-memory tree (Node/Inode); supports multi-level paths, raw modal vi editor, and echo redirection."),
        ("5. Low-Level Append-Only Telemetry (logger.c)", "Every command, timestamp, session ID, and threat event is persisted to logs/session.log via POSIX open(), write(), and fsync()."),
        ("6. Post-Session Forensic Inspector (inspect.sh)", "Automated pipeline chains grep (filtering), sed (normalization), and awk (aggregation) with shell traps to produce incident reports.")
    ]

    for idx, (title, desc) in enumerate(diag_steps):
        cell = table_diag.cell(idx, 0)
        set_cell_background(cell, "F4F6F9" if idx % 2 == 0 else "FFFFFF")
        set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r_t = p.add_run(title + "\n")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(0, 32, 96)
        r_d = p.add_run(desc)
        r_d.font.name = "Times New Roman"
        r_d.font.size = Pt(10.5)

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(4)
    p_cap.paragraph_format.space_after = Pt(10)
    r_cap = p_cap.add_run("Figure 2.1: Architectural Workflow and Data Pipeline of IntruderFound")
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(10)
    r_cap.font.italic = True

    add_subheading("2.2 Tool and Technique Selection")
    add_body_p(
        "The technologies powering IntruderFound were selected based on low-level systems control, standard compliance, and execution efficiency:"
    )
    add_bullet("Provides unmanaged memory control, direct access to POSIX kernel system calls, raw terminal mode manipulation via termios.h, and deterministic real-time execution.", bold_prefix="C Programming Language (C11 / POSIX.1-2008): ")
    add_bullet("Strict compiler diagnostics (-Wall -Wextra -std=c11) ensure memory safety, type cleanliness, and cross-platform portability between Linux and macOS.", bold_prefix="GCC Toolchain & GNU Make: ")
    add_bullet("Leverages the classic UNIX philosophy of chaining small, specialized tools (grep for line matching, sed for delimiter standardization, and awk for associative array aggregation and duration math).", bold_prefix="POSIX Shell Scripting (Bash, awk, sed, grep): ")

    add_subsubheading("Application of Object-Oriented Programming (OOP) Concepts in C:")
    add_body_p(
        "Although the C language does not provide native object-oriented syntax (such as classes or access specifiers), "
        "IntruderFound rigorously implements core Object-Oriented Programming paradigms through modular data abstraction, "
        "structural composition, and encapsulation:"
    )
    add_bullet(
        "Internal subsystem states—such as the log file descriptor (log_fd), session token (session_id), original terminal settings (orig_termios), and signal flags (pending_signal)—are declared with static file scope inside their respective .c units. They can only be manipulated through strict public interface functions defined in header files (.h), perfectly emulating private class member encapsulation.",
        bold_prefix="1. Encapsulation & Information Hiding: "
    )
    add_bullet(
        "The virtual file system models real-world UNIX files and directories through structured composition. An Inode struct encapsulates file metadata (permissions, owner, group, size, mtime, and data buffer), while a Node struct models the directory tree entry. This decoupled association directly reflects the entity-component architecture in object modeling.",
        bold_prefix="2. Object Modeling via Struct Composition: "
    )
    add_code_block(
        "typedef struct Inode {\n"
        "    int ino;\n"
        "    int is_directory;\n"
        "    mode_t mode;        // POSIX permission bits (0755, 0644)\n"
        "    char owner[32];     // e.g., 'user123'\n"
        "    char group[32];     // e.g., 'user123'\n"
        "    size_t size;\n"
        "    time_t mtime;\n"
        "    char content[1024]; // File payload\n"
        "} Inode;\n\n"
        "typedef struct Node {\n"
        "    char name[64];\n"
        "    Inode *inode;       // Aggregation of Inode object\n"
        "    struct Node *parent;\n"
        "    struct Node *children;\n"
        "    struct Node *next;\n"
        "} Node;"
    )
    add_bullet(
        "Memory allocation for nodes and inodes is governed strictly by factory functions (create_inode(), create_node()), acting as parameterized constructors that initialize all fields safely. Memory reclamation is executed via systematic tree deallocation routines, functioning as object destructors.",
        bold_prefix="3. Constructors and Destructors (Abstract Data Types): "
    )
    add_bullet(
        "The file system traversal engine treats Node objects polymorphically: functions inspect node->inode->is_directory at runtime to dynamically branch between directory-stream listing (list_directory) or file-content streaming (cat / open_editor).",
        bold_prefix="4. Polymorphic Behavior: "
    )

    # -------------------------------------------------------------
    # CHAPTER 3: IMPLEMENTATION & TESTING
    # -------------------------------------------------------------
    add_chapter_heading("Chapter 3: Implementation & Testing")

    add_subheading("3.1 Experimental Setup")
    add_body_p(
        "The project was implemented, compiled, and benchmarked within a standard UNIX systems development environment:"
    )
    add_bullet("macOS Darwin (Apple Silicon, ARM64) and Ubuntu Linux 22.04 LTS (x86_64).", bold_prefix="Host Platforms: ")
    add_bullet("Apple clang version 15.0.0 / GNU GCC version 11.4.0.", bold_prefix="Compiler Infrastructure: ")
    add_bullet("GNU Make 3.81 (macOS native) and GNU Make 4.3 (Linux).", bold_prefix="Build Automation: ")
    add_bullet("ANSI-compliant VT100 / xterm-256color terminal emulator.", bold_prefix="Terminal Environment: ")
    add_bullet("-Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE", bold_prefix="Compiler Directives: ")

    add_subheading("3.2 Results (Test Cases & Output Verification)")
    add_body_p(
        "Table 3.1 details the systematic verification matrix conducted across all core modules, demonstrating complete "
        "conformance with POSIX standards and honeypot deception requirements."
    )

    # Test Table
    table_tests = doc.add_table(rows=15, cols=5)
    table_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_tests, "B0C4DE")

    t_headers = ["Test ID", "Module Under Test", "Input Command / Action", "Expected Result", "Status"]
    for j, h in enumerate(t_headers):
        cell = table_tests.cell(0, j)
        set_cell_background(cell, "002060")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    test_matrix = [
        ("TC-01", "Identity", "whoami, id, uname -a", "Emulates user123 (UID 1001) on srv-node01", "PASS"),
        ("TC-02", "Path Navigation", "cd Documents && pwd", "Resolves path to /home/user123/Documents", "PASS"),
        ("TC-03", "VFS Metadata", "ls -la", "Displays POSIX listing with drwxr-xr-x & sizes", "PASS"),
        ("TC-04", "Redirection", "echo 'secret' > key.txt", "Creates inode, writes buffer, readable via cat", "PASS"),
        ("TC-05", "Appending", "echo 'extra' >> key.txt", "Appends newline and content safely without overflow", "PASS"),
        ("TC-06", "File Ops", "cp key.txt copy.txt && rm copy.txt", "Duplicates inode content; removes file cleanly", "PASS"),
        ("TC-07", "VI Editor Trap", "vi secrets.txt", "Raw terminal mode; real Esc key; saves on :wq", "PASS"),
        ("TC-08", "Privilege Deception", "sudo su", "Prompts for password; returns authentic 3 failed attempts", "PASS"),
        ("TC-09", "Destructive Check", "rm -rf /", "Emits dangerous operation warning; zero honeypot leak", "PASS"),
        ("TC-10", "Sensitive Files", "cat /etc/shadow", "Returns authentic 'Permission denied'", "PASS"),
        ("TC-11", "False Positive", "echo 'pseudo code'", "Allows innocent commands containing 'sudo' substring", "PASS"),
        ("TC-12", "Signal Interception", "Ctrl+C (SIGINT)", "Intercepts signal; prints ^C; reissues prompt cleanly", "PASS"),
        ("TC-13", "POSIX Logger", "Runtime activity", "Writes via open, write, fsync with path resolution", "PASS"),
        ("TC-14", "Analytics Suite", "make inspect", "Parses logs; calculates exact duration; writes MD/TXT", "PASS")
    ]

    for i, (tid, mod, inp, exp, stat) in enumerate(test_matrix):
        row = table_tests.rows[i + 1]
        bg = "F9FAFC" if i % 2 == 0 else "FFFFFF"
        for j, val in enumerate([tid, mod, inp, exp, stat]):
            cell = row.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
            p = cell.paragraphs[0]
            if j in (0, 4):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if j == 4:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 128, 0)

    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(4)
    p_tcap.paragraph_format.space_after = Pt(12)
    r_tcap = p_tcap.add_run("Table 3.1: Systematic Functional Verification Matrix for IntruderFound")
    r_tcap.font.name = "Times New Roman"
    r_tcap.font.size = Pt(10)
    r_tcap.font.italic = True

    add_subsubheading("Verified Interactive Terminal Execution:")
    add_code_block(
        "user123@srv-node01:~$ whoami\n"
        "user123\n\n"
        "user123@srv-node01:~$ id\n"
        "uid=1001(user123) gid=1001(user123) groups=1001(user123)\n\n"
        "user123@srv-node01:~$ pwd\n"
        "/home/user123\n\n"
        "user123@srv-node01:~$ ls -la\n"
        "total 9\n"
        "drwxr-xr-x 1 user123  user123    4096 Nov 23 00:33 Documents/\n"
        "drwxr-xr-x 1 user123  user123    4096 Nov 23 00:33 Downloads/\n"
        "-rw------- 1 user123  user123      47 Nov 23 00:33 secrets.txt\n\n"
        "user123@srv-node01:~$ sudo su\n"
        "[sudo] password for user123: \n"
        "sudo: 3 incorrect password attempts\n\n"
        "user123@srv-node01:~$ rm -rf /\n"
        "rm: it is dangerous to operate recursively on '/'\n"
        "rm: use --no-preserve-root to override this failsafe\n\n"
        "user123@srv-node01:~$ exit\n"
        "logout"
    )

    add_subsubheading("Generated Forensic Incident Summary (make inspect):")
    add_code_block(
        "======================================================================\n"
        "                 INTRUDERFOUND FORENSIC SESSION REPORT                \n"
        "======================================================================\n\n"
        "1. EXECUTIVE SUMMARY\n"
        "----------------------------------------------------------------------\n"
        "Total Tracked Sessions   : 6\n"
        "Total Commands Executed  : 48\n"
        "Suspicious Incidents     : 7\n"
        "Intercepted Signals      : 2\n\n"
        "2. SUSPICIOUS INCIDENTS & THREAT ALERTS\n"
        "----------------------------------------------------------------------\n"
        "[01] 2026-11-23 00:28:39 | Threat: Privilege escalation attempt (sudo)\n"
        "[02] 2026-11-23 00:33:56 | Threat: Sensitive system file access (/etc/shadow)\n"
        "[03] 2026-11-23 00:33:56 | Threat: Destructive file operation (rm -rf)\n\n"
        "3. SESSION TIMELINE & DURATION\n"
        "----------------------------------------------------------------------\n"
        "Session: 2026_11_23_00_37_13_43402\n"
        "  Start   : 2026-11-23 00:37:13\n"
        "  End     : 2026-11-23 00:39:52\n"
        "  Duration: 2m 39s (Completed)\n"
        "======================================================================"
    )

    # -------------------------------------------------------------
    # CHAPTER 4: CONCLUSION & FUTURE SCOPE
    # -------------------------------------------------------------
    add_chapter_heading("Chapter 4: Conclusion & Future Scope")

    add_subheading("4.1 Summary of Work and Achievements")
    add_body_p(
        "The IntruderFound project successfully bridged low-level UNIX systems programming with practical cybersecurity defense. "
        "Through disciplined engineering, the team accomplished the following deliverables:"
    )
    add_bullet("Delivered a believable Linux command-line decoy that actively deceives unauthorized users without exposing host infrastructure.", bold_prefix="High-Fidelity Shell Emulation: ")
    add_bullet("Leveraged C structs to model inodes and directories, simulating POSIX permission bits, ownership, and multi-level path traversal.", bold_prefix="Robust VFS Architecture: ")
    add_bullet("Implemented a raw-mode termios modal editor trap capable of capturing literal escape sequences.", bold_prefix="Interactive vi Trap: ")
    add_bullet("Employed POSIX sigaction to eliminate process breaks on SIGINT, SIGTSTP, and SIGHUP.", bold_prefix="Process & Signal Resilience: ")
    add_bullet("Constructed an immutable, append-only logger utilizing POSIX open(), write(), and fsync() system calls with binary path self-resolution.", bold_prefix="Kernel-Level I/O Logging: ")
    add_bullet("Created a Bash/awk forensics pipeline that computes session durations and exports structured incident reports in Markdown and plain text.", bold_prefix="Automated Forensic Analytics: ")

    add_body_p(
        "The disciplined adoption of Object-Oriented Programming (OOP) concepts within the C codebase—specifically through "
        "data encapsulation, struct composition, parameterized constructors, and polymorphic node dispatch—directly enabled "
        "modular testing and seamless team collaboration across all five subsystems."
    )

    add_subheading("4.2 Impact on Society, Environmental Sustainability & Ethical Compliance")
    add_body_p(
        "From a societal perspective, IntruderFound provides defensive administrators and researchers with deep post-exploitation "
        "forensic intelligence, enabling timely patching of zero-day entry points. Environmentally, because the honeypot runs "
        "as a lightweight in-memory C binary, it consumes negligible power compared to full hardware virtual machines, reducing "
        "server energy consumption. Ethically, the system operates strictly within a contained, passive observation sandbox. "
        "It performs no unauthorized external network scanning, counter-attacks, or offensive exploits, adhering fully to cybersecurity research ethics."
    )

    add_subheading("4.3 Limitations of the Work and Future Scope")
    add_body_p(
        "While the current implementation fulfills all project-based learning objectives, several boundaries exist:"
    )
    add_bullet("The virtual file system resides entirely in heap memory and resets when the process terminates.", bold_prefix="In-Memory Volatility: ")
    add_bullet("I/O redirection currently supports file overwrite (>) and append (>>), but does not yet emulate inter-process pipes (|).", bold_prefix="Pipeline Emulation: ")

    add_subsubheading("Future Enhancements:")
    add_bullet("Integrating a lightweight pseudo-SSH daemon using libssh to expose the decoy shell over network port 2222, automatically trapping remote botnets.", bold_prefix="1. Network Daemon Integration: ")
    add_bullet("Serializing in-memory inode states to an encrypted SQLite database on disk so virtual environments persist across sessions.", bold_prefix="2. Persistent Mock Storage: ")
    add_bullet("Configuring real-time webhook dispatch to forward forensic event logs to enterprise SIEM platforms (Splunk, ElasticSearch).", bold_prefix="3. SIEM Stream Integration: ")

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_chapter_heading("References")
    references = [
        "[1] W. R. Stevens and S. A. Rago, Advanced Programming in the UNIX Environment, 3rd ed. Boston, MA: Addison-Wesley, 2013.",
        "[2] M. Kerrisk, The Linux Programming Interface: A Linux and UNIX System Programming Handbook. San Francisco, CA: No Starch Press, 2010.",
        "[3] L. Spitzner, Honeypots: Tracking Hackers. Boston, MA: Addison-Wesley, 2003.",
        "[4] IEEE Computer Society, Standard for Information Technology—Portable Operating System Interface (POSIX®) Base Specifications, Issue 7, IEEE Std 1003.1-2008, 2018.",
        "[5] D. Dougherty and A. Robbins, sed & awk, 2nd ed. Sebastopol, CA: O'Reilly Media, 1997."
    ]
    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.25
        r_ref = p_ref.add_run(ref)
        r_ref.font.name = "Times New Roman"
        r_ref.font.size = Pt(11)

    # -------------------------------------------------------------
    # APPENDIX: TEAM ROLES AND CONTRIBUTIONS
    # -------------------------------------------------------------
    add_chapter_heading("Appendix: Team Roles and Contributions")
    add_body_p("The project workload was distributed among the team of five members according to functional subsystem specializations:")

    contributions = [
        ("Dhruv Mittal (Lead Architecture & Standard I/O Engineer):",
         "Architected the primary interactive Read-Eval-Print Loop (REPL) in C. Configured GNU Make and GCC build automation with strict POSIX compliance flags. Managed standard I/O buffer flushing (fflush) and terminal prompt authenticity. Coordinated system-level module integration."),
        ("Riddhi Jaggi (Virtual File System & Inode Architect):",
         "Designed the in-memory virtual directory hierarchy using C structs (Inode and Node abstractions). Implemented POSIX file permission modeling (mode_t), timestamps, and ownership attributes. Developed multi-level recursive path resolution (resolve_path) and POSIX formatted directory listing (ls -la)."),
        ("Shourya Somani (Editor Trap & Command Dispatcher):",
         "Engineered the simulated modal vi editor trap utilizing termios raw mode and escape sequence handling. Implemented command dispatch routines for file manipulation (touch, cat, rm, cp, mv). Developed safe in-memory stream redirection (> and >>) with buffer overflow protection."),
        ("Navneet Patel (POSIX System Calls & Signal Security Lead):",
         "Implemented signal interception routines using POSIX sigaction for SIGINT, SIGTSTP, and SIGHUP. Developed the append-only audit logging engine using low-level POSIX file descriptors (open, write, fsync). Engineered dynamic executable path self-resolution (_NSGetExecutablePath / /proc/self/exe) for persistent logging."),
        ("Priyanshi Sharma (Telemetry Analyst & Shell Automation Engineer):",
         "Engineered the backend automated forensic analytics pipeline (scripts/inspect.sh). Chained grep, sed, and awk filters to extract telemetry metrics and calculate command frequency distributions. Implemented portable epoch timestamp math for session duration tracking and automated Markdown and plain text report generation.")
    ]

    for title, desc in contributions:
        add_bullet(desc, bold_prefix=title + " ")

    # Save document
    output_path = "/Users/dhruv/IntruderFound/docs/IntruderFound_Project_Report.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    create_report()
