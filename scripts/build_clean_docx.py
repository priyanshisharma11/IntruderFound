import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
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

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
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

def generate_report():
    doc = Document()

    # Section Settings: A4 with 2.0 cm margins on all sides (Standard JIIT Format)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    # Footer Setup: Times New Roman, pure black, bottom-centered page number
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_para.add_run()
    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(10)
    footer_run.font.color.rgb = RGBColor(0, 0, 0)
    add_page_number(footer_run)

    # Base Normal Style: Times New Roman, pure black, 1.5 line spacing
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)

    def p_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_chapter(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_heading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_subheading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_body(text, bold_prefix=None, space_after=6):
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
            r_pre.font.color.rgb = RGBColor(0, 0, 0)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_bullet(text, bold_prefix=None):
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
            r_pre.font.color.rgb = RGBColor(0, 0, 0)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def p_code_box(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F7F7F7")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            </w:tblBorders>
        ''')
        tblPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(code_text)
        r.font.name = "Courier New"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0, 0, 0)
        # Empty space after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(4)

    def p_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.font.italic = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return p

    # =============================================================
    # COVER / TITLE PAGE (Matches Visual Style of User's Reference PDF)
    # =============================================================
    p_title("Jaypee Institute of Information Technology")
    p_subtitle("Sector-62, Noida")
    p_subtitle("Department of Computer Science and Engineering and\nInformation Technology")

    if os.path.exists("/tmp/jiit_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(8)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture("/tmp/jiit_logo.png", width=Inches(1.8))

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(4)
    p_proj.paragraph_format.space_after = Pt(12)
    
    r_on = p_proj.add_run("Project Report\nOn\n")
    r_on.font.name = "Times New Roman"
    r_on.font.size = Pt(13)
    r_on.font.bold = True
    r_on.font.color.rgb = RGBColor(0, 0, 0)

    r_pname = p_proj.add_run("IntruderFound – Interactive Command-Line Honeypot & Attacker Session\nInspector\n")
    r_pname.font.name = "Times New Roman"
    r_pname.font.size = Pt(14)
    r_pname.font.bold = True
    r_pname.font.underline = True
    r_pname.font.color.rgb = RGBColor(0, 0, 0)

    r_crs = p_proj.add_run("UNIX PROGRAMMING LAB (Course Code: 24B15CS214)\nSession: Odd Semester\n(2026-2027)")
    r_crs.font.name = "Times New Roman"
    r_crs.font.size = Pt(12)
    r_crs.font.bold = True
    r_crs.font.color.rgb = RGBColor(0, 0, 0)

    # Submitted By and Submitted To block (clean text columns, strictly no tables)
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(16)
    p_sub.paragraph_format.space_after = Pt(0)
    p_sub.paragraph_format.line_spacing = 1.25
    
    r_sub = p_sub.add_run(
        "Submitted by:\t\t\t\t\tSubmitted to:\n"
        "Priyanshi Sharma\t2501030218\t\tMr. Baibhav Singh\n"
        "Shourya Somani\t2501030221\n"
        "Navneet Patel\t2501030227\n"
        "Riddhi Jaggi\t\t2501030232\n"
        "Dhruv Mittal\t\t2501030233\n\n"
        "Batch: B5"
    )
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # =============================================================
    # TABLE OF CONTENTS
    # =============================================================
    p_chapter("Table of Contents")
    toc_items = [
        ("Chapter 1: Introduction", "1"),
        ("  1.1 Background", "1"),
        ("  1.2 Problem Statement", "1"),
        ("  1.3 Social & Environmental Relevance (SDGs)", "2"),
        ("  1.4 Scope and Requirements", "2"),
        ("Chapter 2: System Design & Methodology", "4"),
        ("  2.1 Proposed Methodology and Architecture Flow", "4"),
        ("  2.2 Tool and Technique Selection", "5"),
        ("  2.3 Implementation of Object-Oriented Concepts in C", "6"),
        ("Chapter 3: Implementation & Testing", "7"),
        ("  3.1 Experimental Setup", "7"),
        ("  3.2 Results and Verification Matrix", "7"),
        ("  3.3 Demonstration Walkthrough and Output Verification", "9"),
        ("Chapter 4: Conclusion & Future Scope", "11"),
        ("  4.1 Summary of Work and Achievements", "11"),
        ("  4.2 Societal Impact, Sustainability, and Ethical Compliance", "11"),
        ("  4.3 Limitations and Future Scope", "12"),
        ("References", "13"),
        ("Appendix: Team Roles and Contributions", "14")
    ]
    for item, pg in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(2)
        p_t.paragraph_format.line_spacing = 1.15
        r1 = p_t.add_run(item)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(0, 0, 0)
        if not item.startswith("  "):
            r1.font.bold = True

    doc.add_page_break()

    # =============================================================
    # CHAPTER 1: INTRODUCTION
    # =============================================================
    p_chapter("Chapter 1: Introduction")

    p_heading("1.1 Background")
    p_body(
        "Command-line interfaces are commonly used to administer Linux and UNIX-like systems. A terminal provides direct access "
        "to utilities for navigating directories, viewing files, changing permissions, managing users, and performing administrative tasks. "
        "This flexibility is useful, but it also means that commands entered into a real system can have severe consequences. In a security-learning "
        "context, it is useful to observe how a user explores an environment without exposing a real operating system or important files to "
        "potentially destructive commands."
    )
    p_body(
        "A honeypot is a decoy system or service intended to attract, detect, or study unauthorized activity. Traditional honeypots may imitate "
        "services or entire systems and record interaction. IntruderFound adopts this idea at a local, command-line level. It offers a simulated "
        "POSIX terminal environment with a defined command set and a recording and inspection pipeline. Developed in C with a post-session analytics "
        "engine in Bash, IntruderFound presents an authentic decoy terminal (user123@srv-node01:~$ ) that emulates native Linux behavior, "
        "intercepts signals, contains file manipulations inside an in-memory Virtual File System, and silently logs telemetry for automated analysis."
    )

    p_heading("1.2 Problem Statement")
    p_body(
        "Demonstrating suspicious terminal behavior on a real system can be risky and difficult to repeat consistently. Destructive commands "
        "(e.g., rm -rf /), administrative privilege escalation (sudo, su), or commands that access sensitive locations (/etc/shadow) should not be "
        "casually executed during classroom demonstrations. In addition, raw command history (.bash_history) alone is easily purged, tampered with, "
        "and inconvenient to analyze after a session. Conventional demonstrations face three primary challenges:"
    )
    p_bullet(
        "Executing commands against the host OS permits genuine host modifications, creating risks of malware execution or accidental data loss.",
        bold_prefix="1. Lack of Virtual Isolation: "
    )
    p_bullet(
        "Simulators that output overt alert warnings (such as '[SECURITY ALERT] Suspicious command detected!') alert the intruder immediately, destroying the honeypot deception and terminating the interaction prematurely.",
        bold_prefix="2. The Honeypot Paradox: "
    )
    p_bullet(
        "Raw audit trails are cumbersome to evaluate manually without an automated tool to aggregate command distributions and compute session metrics.",
        bold_prefix="3. Lack of Forensic Automation: "
    )
    p_body(
        "IntruderFound addresses this learning problem by providing a contained, simulated terminal experience that supports selected normal interactions, "
        "detects suspicious command patterns using tokenized rules, handles signals gracefully, responds with authentic Linux error messages, "
        "and generates comprehensive summary reports."
    )

    p_heading("1.3 Social & Environmental Relevance")
    p_body(
        "Cybersecurity attacks against public infrastructure, educational networks, and enterprises cause significant operational disruption. "
        "By providing a lightweight, open-source educational honeypot, IntruderFound democratizes threat observation without requiring "
        "expensive commercial software or high-end multi-node virtualization servers. From an environmental perspective, running in-memory "
        "C simulations consumes negligible CPU cycles and memory compared to heavy hardware virtual machines (VMs), lowering the compute and carbon "
        "footprint of continuous defensive security monitoring."
    )
    p_subheading("Primary Sustainable Development Goals (SDGs):")
    p_bullet("Promotes resilient technological infrastructure, secure computing environments, and proactive defense against unauthorized digital intrusion.", bold_prefix="SDG 9 (Industry, Innovation and Infrastructure): ")
    p_bullet("Strengthens institutional defense capabilities and transparency against cybercrime through immutable forensic logging and accountability.", bold_prefix="SDG 16 (Peace, Justice and Strong Institutions): ")
    p_subheading("Secondary Sustainable Development Goals (SDGs):")
    p_bullet("Serves as an educational framework for teaching low-level POSIX concepts, signal processing, and defensive systems engineering.", bold_prefix="SDG 4 (Quality Education): ")

    p_heading("1.4 Scope and Requirements")
    p_body(
        "IntruderFound is limited to a local educational simulation. It imitates a small subset of terminal behavior and records user activity "
        "within its own application. It encompasses:"
    )
    p_bullet("An interactive decoy shell loop presenting an authentic non-root user prompt (user123@srv-node01:~$ ).", bold_prefix="Interactive Prompt: ")
    p_bullet("An in-memory Virtual File System (VFS) with struct Inode and struct Node, supporting permissions (mode_t), timestamps, ownership, and multi-level path resolution (cd, ls -la, pwd, mkdir, touch, cat, rm, cp, mv).", bold_prefix="Virtual File Operations: ")
    p_bullet("In-memory stream redirection (> and >>) with strict buffer-overflow protections.", bold_prefix="Stream Redirection: ")
    p_bullet("A modal text editor using termios raw mode, capturing the physical Escape key (0x1B), and handling :w, :q, :wq, and :q!.", bold_prefix="Simulated VI Editor: ")
    p_bullet("Asynchronous signal interception (SIGINT, SIGTSTP, SIGHUP) via POSIX sigaction, reissuing fresh prompts without terminating.", bold_prefix="Signal Handling: ")
    p_bullet("Context-aware command tokenization that simulates authentic Linux errors (sudo: 3 incorrect password attempts, Permission denied) rather than warning the adversary.", bold_prefix="Honeypot Deception Engine: ")
    p_bullet("Low-level POSIX system call logging (open, write, fsync) with binary path resolution for guaranteed log persistence.", bold_prefix="Session Logging: ")
    p_bullet("A pipelined analytics utility combining grep, sed, and awk with POSIX traps to compute session durations and generate Markdown and text incident reports.", bold_prefix="Inspection Pipeline: ")
    p_body(
        "Safety Boundary: The application keeps simulated command text strictly inside its own logic. It does not pass raw user input to a real shell for execution, nor does it provide an untrusted remote network listener."
    )

    # =============================================================
    # CHAPTER 2: SYSTEM DESIGN & METHODOLOGY
    # =============================================================
    p_chapter("Chapter 2: System Design & Methodology")

    p_heading("2.1 Proposed Methodology and Architecture Flow")
    p_body(
        "The application is organized around a central control module. The main program reads input, performs logging and security checks, "
        "and routes accepted input to the appropriate simulated command behavior. The editor, logger, security detector, and signal handling code "
        "are separated into modules so that the main program can coordinate them without duplicating all implementation details. "
        "The overall processing flow is illustrated in Figure 1 below:"
    )

    if os.path.exists("/tmp/intruderfound_architecture.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        r_img = p_img.add_run()
        r_img.add_picture("/tmp/intruderfound_architecture.png", width=Inches(6.2))
        p_caption("Figure 1: IntruderFound processing flow, from user input through signal interception, deception checks, and VFS execution, to post-session forensic inspection.")

    p_body(
        "As illustrated in Figure 1, user keystrokes enter the REPL in main.c. The signal shield (signals.c) intercepts terminal interrupts. "
        "The security detector (security.c) inspects tokenized command verbs: recognized threats trigger authentic simulated Linux errors. "
        "Safe commands operate upon the in-memory tree hierarchy. Simultaneously, all events are piped to the append-only log via logger.c. "
        "Finally, inspect.sh parses the log file offline to produce comprehensive forensic incident reports."
    )

    p_heading("2.2 Tool and Technique Selection")
    p_body(
        "The development stack was selected based on systems-level control, standards compliance, and execution efficiency:"
    )
    p_bullet("Chosen for unmanaged memory control, low-level POSIX system calls, terminal termios configuration, and minimal CPU footprint.", bold_prefix="C Programming Language (C11 / POSIX.1-2008): ")
    p_bullet("Provides strict compiler diagnostics (-Wall -Wextra -std=c11) and reproducible automated builds across Linux and macOS.", bold_prefix="GCC Toolchain & GNU Make: ")
    p_bullet("Implements the UNIX philosophy of pipelining modular text-stream processors (grep for filtering, sed for normalization, and awk for associative array calculations).", bold_prefix="POSIX Shell Scripting (Bash, awk, sed, grep): ")

    p_heading("2.3 Implementation of Object-Oriented Concepts in C")
    p_body(
        "Although compiled procedurally, IntruderFound is structured around core Object-Oriented Programming (OOP) paradigms "
        "to ensure clean abstraction, encapsulation, and maintainability:"
    )
    p_bullet(
        "Internal subsystem states—including the log file descriptor (log_fd), session identifier (session_id), original terminal settings (orig_termios), and signal state (pending_signal)—are declared with static file scope in their respective .c units. They cannot be accessed or altered directly by external modules, enforcing private member encapsulation through public header declarations.",
        bold_prefix="1. Encapsulation & Information Hiding: "
    )
    p_bullet(
        "The virtual file system models real-world UNIX files and directories through object composition. An Inode struct encapsulates metadata (permissions, owner, group, size, mtime, and data buffer), while a Node struct models the directory tree entry. This separation directly mirrors entity-component object modeling.",
        bold_prefix="2. Object Modeling via Struct Composition: "
    )
    p_code_box(
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
    p_bullet(
        "Creation of inodes and directory nodes is mediated by factory functions (create_inode(), create_node()), acting as parameterized constructors that ensure valid state initialization. Systematic tree deallocation routines act as object destructors.",
        bold_prefix="3. Constructors and Destructors (ADTs): "
    )
    p_bullet(
        "Node traversal functions inspect node->inode->is_directory at runtime, dynamically branching between directory stream listing (list_directory) and file buffer reading (cat / open_editor), demonstrating runtime polymorphic dispatch.",
        bold_prefix="4. Polymorphism: "
    )

    # =============================================================
    # CHAPTER 3: IMPLEMENTATION & TESTING
    # =============================================================
    p_chapter("Chapter 3: Implementation & Testing")

    p_heading("3.1 Experimental Setup")
    p_body(
        "The system was compiled and evaluated in a standard POSIX UNIX environment:"
    )
    p_bullet("macOS Darwin (Apple Silicon, ARM64) and Ubuntu Linux 22.04 LTS (x86_64).", bold_prefix="Host Environments: ")
    p_bullet("Apple clang 15.0+ / GNU GCC 11.4+.", bold_prefix="Compiler Toolchain: ")
    p_bullet("GNU Make 3.81 (macOS native) and GNU Make 4.3 (Linux).", bold_prefix="Build Automation: ")
    p_bullet("xterm-256color compliant terminal emulator with termios raw-mode support.", bold_prefix="Terminal Interface: ")
    p_bullet("-Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE", bold_prefix="Compiler Flags: ")

    p_heading("3.2 Results (Verification Matrix)")
    p_body(
        "The application was subjected to functional verification covering identity emulation, VFS manipulation, stream redirection, "
        "vi modal editing, deception logic, signal handling, low-level logging, and forensic report generation. Table 1 outlines the verified test cases."
    )

    # Table 1: Testing Matrix
    table_tests = doc.add_table(rows=15, cols=5)
    table_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_tests)

    headers = ["Test ID", "Module Under Test", "Input Command / Action", "Expected Result", "Status"]
    for j, h in enumerate(headers):
        cell = table_tests.cell(0, j)
        set_cell_background(cell, "F2F2F2")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)

    test_data = [
        ("TC-01", "Identity", "whoami, id, uname -a", "Emulates user123 (UID 1001) on srv-node01", "PASS"),
        ("TC-02", "Path Navigation", "cd Documents && pwd", "Resolves path to /home/user123/Documents", "PASS"),
        ("TC-03", "VFS Metadata", "ls -la", "Displays POSIX listing with drwxr-xr-x & sizes", "PASS"),
        ("TC-04", "Redirection", "echo 'secret' > key.txt", "Creates inode, writes buffer, readable via cat", "PASS"),
        ("TC-05", "Appending", "echo 'extra' >> key.txt", "Appends newline and content safely without overflow", "PASS"),
        ("TC-06", "File Operations", "cp key.txt copy.txt && rm copy.txt", "Duplicates inode content; removes file cleanly", "PASS"),
        ("TC-07", "VI Editor Trap", "vi secrets.txt", "Raw terminal mode; real Esc key; saves on :wq", "PASS"),
        ("TC-08", "Privilege Deception", "sudo su", "Prompts for password; returns authentic 3 failed attempts", "PASS"),
        ("TC-09", "Destructive Check", "rm -rf /", "Emits dangerous operation warning; zero honeypot leak", "PASS"),
        ("TC-10", "Sensitive Files", "cat /etc/shadow", "Returns authentic 'Permission denied'", "PASS"),
        ("TC-11", "False Positive", "echo 'pseudo code'", "Allows innocent commands containing 'sudo' substring", "PASS"),
        ("TC-12", "Signal Interception", "Ctrl+C (SIGINT)", "Intercepts signal; prints ^C; reissues prompt cleanly", "PASS"),
        ("TC-13", "POSIX Logger", "Runtime activity", "Writes via open, write, fsync with path resolution", "PASS"),
        ("TC-14", "Analytics Suite", "make inspect", "Parses logs; calculates exact duration; writes MD/TXT", "PASS")
    ]

    for i, (tid, mod, inp, exp, stat) in enumerate(test_data):
        row = table_tests.rows[i + 1]
        for j, val in enumerate([tid, mod, inp, exp, stat]):
            cell = row.cells[j]
            set_cell_margins(cell, top=40, bottom=40, left=60, right=60)
            p = cell.paragraphs[0]
            if j in (0, 4):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(0, 0, 0)
            if j == 4:
                r.font.bold = True

    p_caption("Table 1: Functional verification matrix of IntruderFound.")

    p_heading("3.3 Demonstration Walkthrough and Output Verification")
    p_body(
        "Below is an excerpt from a verified live test session demonstrating identity emulation, file creation, "
        "and honeypot deception without alarming the intruder:"
    )
    p_code_box(
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
        "user123@srv-node01:~$ cat /etc/shadow\n"
        "cat: /etc/shadow: Permission denied\n\n"
        "user123@srv-node01:~$ rm -rf /\n"
        "rm: it is dangerous to operate recursively on '/'\n"
        "rm: use --no-preserve-root to override this failsafe\n\n"
        "user123@srv-node01:~$ exit\n"
        "logout"
    )

    p_body(
        "Executing 'make inspect' immediately parses the session log and outputs the following forensic summary:"
    )
    p_code_box(
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

    # =============================================================
    # CHAPTER 4: CONCLUSION & FUTURE SCOPE
    # =============================================================
    p_chapter("Chapter 4: Conclusion & Future Scope")

    p_heading("4.1 Summary of Work and Achievements")
    p_body(
        "IntruderFound demonstrates a small command-line honeypot simulation with an interactive decoy shell and an activity-inspection pipeline. "
        "The project brings together C programming, modular design, command handling, a simulated file system, a VI-inspired editor, "
        "event logging, rule-based suspicious-command detection, signal handling, Bash scripting, AWK text processing, and Makefile automation."
    )
    p_body(
        "The main value of the project is educational integration: the user can interact with a simulated terminal, see suspicious patterns blocked, "
        "inspect the recorded events, and generate a report. This provides a repeatable demonstration without intentionally executing entered commands "
        "as real operating-system commands. Testing recorded in the project documentation confirms the main demo paths in the development environment."
    )
    p_body(
        "The project is a prototype with clear boundaries, particularly its contained command set and rule-based pattern matching. "
        "Applying Object-Oriented Programming (OOP) concepts in C—specifically through structural encapsulation, data hiding, "
        "and polymorphic node processing—enabled robust modular isolation and seamless collaboration across all five team members."
    )

    p_heading("4.2 Societal Impact, Sustainability, and Ethical Compliance")
    p_body(
        "Security tools should be used responsibly and with authorization. IntruderFound does not collect remote attacker data, credentials, "
        "or network traffic in its current local simulation. The project should be described accurately as an educational decoy shell. "
        "Demonstrations should be performed in the intended environment, and raw command input should never be forwarded to a host shell for execution. "
        "From an environmental sustainability standpoint, running a lightweight in-memory C program eliminates the heavy compute overhead of "
        "multi-gigabyte virtual machines, lowering monitoring power consumption."
    )

    p_heading("4.3 Limitations and Future Scope")
    p_body(
        "The project has established boundaries that offer opportunities for future work:"
    )
    p_bullet("The virtual file system is an in-memory simulation and does not implement a full persistent POSIX file system.", bold_prefix="In-Memory Volatility: ")
    p_bullet("Suspicious detection uses tokenized pattern checks; advanced obfuscation or unknown exploit payloads require deeper inspection.", bold_prefix="Rule-Based Detection: ")
    p_bullet("I/O redirection currently supports file overwrite (>) and append (>>), but does not yet emulate inter-process pipes (|).", bold_prefix="Pipeline Emulation: ")

    p_subheading("Future Enhancements:")
    p_bullet("Expand the virtual file system and command set while maintaining a strict simulation boundary.", bold_prefix="1. Command Set Expansion: ")
    p_bullet("Binding the decoy engine to a lightweight pseudo-SSH daemon using libssh on port 2222 to capture remote botnet attacks over the network.", bold_prefix="2. Network-Facing Prototype: ")
    p_bullet("Serializing in-memory inode states to an encrypted SQLite file so that the virtual environment persists across sessions.", bold_prefix="3. Persistent Storage: ")
    p_bullet("Streaming parsed JSON forensic logs directly to enterprise SIEM platforms (Splunk, ElasticSearch).", bold_prefix="4. SIEM Integration: ")

    # =============================================================
    # REFERENCES
    # =============================================================
    p_chapter("References")
    references = [
        "[1] GCC Documentation — GNU Compiler Collection documentation and compiler usage.",
        "[2] GNU Make Manual — Makefile syntax and build automation.",
        "[3] GNU Bash Reference Manual — Bash shell and scripting concepts.",
        "[4] GNU AWK User's Guide — Text processing and field-based analysis.",
        "[5] Linux man-pages project — Documentation for signal(), sigaction(), and signal-related interfaces.",
        "[6] POSIX documentation — Standard definitions for shell, signals, and system interfaces.",
        "[7] W. R. Stevens and S. A. Rago, Advanced Programming in the UNIX Environment, 3rd ed. Boston, MA: Addison-Wesley, 2013.",
        "[8] Project source repository — IntruderFound source files, README, test cases, and module documentation."
    ]
    for ref in references:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_before = Pt(2)
        p_r.paragraph_format.space_after = Pt(4)
        p_r.paragraph_format.line_spacing = 1.25
        r = p_r.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)

    # =============================================================
    # APPENDIX: TEAM ROLES AND CONTRIBUTIONS
    # =============================================================
    p_chapter("Appendix: Team Roles and Contributions")
    p_body("The project responsibilities were distributed among the five team members according to modular specializations:")

    contributions = [
        ("Dhruv Mittal (2501030233) — Lead Architecture & Standard I/O Engineer:",
         "Architected the primary interactive Read-Eval-Print Loop (REPL) in C. Configured GNU Make and GCC build automation with strict POSIX compliance flags. Managed standard I/O buffer flushing (fflush) and terminal prompt authenticity. Coordinated system-level module integration."),
        ("Riddhi Jaggi (2501030232) — Virtual File System & Inode Architect:",
         "Designed the in-memory virtual directory hierarchy using C structs (Inode and Node abstractions). Implemented POSIX file permission modeling (mode_t), timestamps, and ownership attributes. Developed multi-level recursive path resolution (resolve_path) and POSIX formatted directory listing (ls -la)."),
        ("Shourya Somani (2501030221) — Editor Trap & Command Dispatcher:",
         "Engineered the simulated modal vi editor trap utilizing termios raw mode and escape sequence handling. Implemented command dispatch routines for file manipulation (touch, cat, rm, cp, mv). Developed safe in-memory stream redirection (> and >>) with buffer overflow protection."),
        ("Navneet Patel (2501030227) — POSIX System Calls & Signal Security Lead:",
         "Implemented signal interception routines using POSIX sigaction for SIGINT, SIGTSTP, and SIGHUP. Developed the append-only audit logging engine using low-level POSIX file descriptors (open, write, fsync). Engineered dynamic executable path self-resolution (_NSGetExecutablePath / /proc/self/exe) for persistent logging."),
        ("Priyanshi Sharma (2501030218) — Telemetry Analyst & Shell Automation Engineer:",
         "Engineered the backend automated forensic analytics pipeline (scripts/inspect.sh). Chained grep, sed, and awk filters to extract telemetry metrics and calculate command frequency distributions. Implemented portable epoch timestamp math for session duration tracking and automated Markdown and plain text report generation.")
    ]

    for title, desc in contributions:
        p_bullet(desc, bold_prefix=title + "\n")

    # Save to destination
    out_file = "/Users/dhruv/IntruderFound/docs/IntruderFound_Project_Report.docx"
    doc.save(out_file)
    print(f"Generated clean report at: {out_file}")

if __name__ == "__main__":
    generate_report()
