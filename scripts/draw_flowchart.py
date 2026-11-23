from PIL import Image, ImageDraw, ImageFont
import os

def create_flowchart():
    # Width x Height
    W, H = 1400, 950
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Try loading a system TTF font, else default
    font_paths = [
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/times.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    ]
    font_large = None
    font_med = None
    font_small = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_large = ImageFont.truetype(fp, 26)
                font_med = ImageFont.truetype(fp, 20)
                font_small = ImageFont.truetype(fp, 17)
                break
            except Exception:
                pass
    if not font_large:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    def draw_box(box, title, subtitle=None, is_diamond=False):
        x0, y0, x1, y1 = box
        if is_diamond:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            points = [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]
            draw.polygon(points, outline="black", fill="#FAFAFA", width=2)
        else:
            # Rounded rect or rect
            draw.rectangle([x0, y0, x1, y1], outline="black", fill="#FAFAFA", width=2)

        # Draw text
        lines = [title]
        if subtitle:
            lines.extend(subtitle.split("\n"))
        
        # Calculate vertical centering
        total_h = len(lines) * 24
        cur_y = ((y0 + y1) - total_h) / 2
        for i, line in enumerate(lines):
            f = font_med if i == 0 else font_small
            bbox = draw.textbbox((0, 0), line, font=f)
            w = bbox[2] - bbox[0]
            draw.text(((x0 + x1 - w) / 2, cur_y), line, fill="black", font=f)
            cur_y += 24

    def draw_arrow(p1, p2, text=None):
        draw.line([p1, p2], fill="black", width=2)
        # Arrowhead
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2: # vertical
            if y2 > y1: # downwards
                draw.polygon([(x2 - 6, y2 - 12), (x2 + 6, y2 - 12), (x2, y2)], fill="black")
            else:
                draw.polygon([(x2 - 6, y2 + 12), (x2 + 6, y2 + 12), (x2, y2)], fill="black")
        elif y1 == y2: # horizontal
            if x2 > x1: # rightwards
                draw.polygon([(x2 - 12, y2 - 6), (x2 - 12, y2 + 6), (x2, y2)], fill="black")
            else:
                draw.polygon([(x2 + 12, y2 - 6), (x2 + 12, y2 + 6), (x2, y2)], fill="black")
        
        if text:
            tx = (x1 + x2) / 2 + 8
            ty = (y1 + y2) / 2 - 18
            draw.text((tx, ty), text, fill="black", font=font_small)

    # 1. User Input
    draw_box((100, 50, 360, 130), "User Interaction", "Terminal Keystrokes / Commands")
    
    # 2. Main REPL
    draw_box((460, 50, 740, 130), "Decoy Shell Engine", "main.c (REPL & State Loop)")
    draw_arrow((360, 90), (460, 90))

    # 3. Signal Decision
    draw_box((840, 40, 1100, 140), "Signal Caught?", "SIGINT / SIGTSTP / SIGHUP", is_diamond=True)
    draw_arrow((740, 90), (840, 90))

    # 4. Signal Handler (Right side)
    draw_box((1180, 50, 1360, 130), "Signal Shield", "signals.c: Reissue ^C\nPreserve Prompt")
    draw_arrow((1100, 90), (1180, 90), "Yes")

    # Down from Signal decision to Threat Evaluation
    draw_box((840, 240, 1100, 340), "Suspicious Match?", "security.c: Token Check", is_diamond=True)
    draw_arrow((970, 140), (970, 240), "No")

    # Suspicious -> Authentic Deception (Left)
    draw_box((460, 250, 740, 330), "Authentic Deception", "sudo: 3 failed attempts\nrm -rf /: EBUSY / EPERM")
    draw_arrow((840, 290), (740, 290), "Yes")

    # Safe Command -> In-Memory VFS (Down)
    draw_box((840, 440, 1100, 520), "In-Memory VFS Dispatch", "Node & Inode Tree\nRaw Modal vi / Redirection")
    draw_arrow((970, 340), (970, 440), "No")

    # Both Deception and VFS feed into Logger
    draw_box((460, 440, 740, 520), "POSIX Telemetry Logger", "logger.c: open, write, fsync\nPath Self-Resolution")
    draw_arrow((600, 330), (600, 440))
    draw_arrow((840, 480), (740, 480))
    # Signal shield also logs
    draw.line([(1270, 130), (1270, 410), (740, 410)], fill="black", width=2)
    draw_arrow((740, 410), (740, 440))

    # Telemetry Log File (Cylinder-like)
    draw_box((460, 600, 740, 670), "Append-Only Audit Log", "logs/session.log")
    draw_arrow((600, 520), (600, 600))

    # Divider line for offline forensic inspection
    draw.line([(80, 720), (1320, 720)], fill="#888888", width=1)
    draw.text((100, 725), "OFFLINE POST-SESSION FORENSIC INSPECTION PIPELINE", fill="#444444", font=font_small)

    # Forensic Inspector Script
    draw_box((300, 770, 600, 850), "Session Inspector", "scripts/inspect.sh\n(grep | sed | awk | trap)")
    draw_arrow((600, 670), (450, 770))

    # Reports
    draw_box((700, 770, 1020, 850), "Automated Forensic Reports", "Text: session_report.txt\nMarkdown: session_report.md")
    draw_arrow((600, 810), (700, 810))

    img.save("/tmp/intruderfound_architecture.png")
    print("Flowchart generated at /tmp/intruderfound_architecture.png")

if __name__ == "__main__":
    create_flowchart()
