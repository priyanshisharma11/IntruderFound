#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include "editor.h"

#define MAX_BUFFER 2048

static struct termios orig_termios;
static int raw_mode_active = 0;

static void disable_raw_mode(void)
{
    if (raw_mode_active)
    {
        tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
        raw_mode_active = 0;
    }
}

static void enable_raw_mode(void)
{
    if (!isatty(STDIN_FILENO))
    {
        return;
    }

    if (tcgetattr(STDIN_FILENO, &orig_termios) == -1)
    {
        return;
    }

    struct termios raw = orig_termios;
    // Disable canonical mode, echo, and signals in editor
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_iflag &= ~(IXON | ICRNL);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw) != -1)
    {
        raw_mode_active = 1;
    }
}

static void render_screen(const char *filename, const char *buffer, int mode, const char *status_msg)
{
    // Clear screen and move cursor to home
    write(STDOUT_FILENO, "\033[2J\033[H", 7);

    // Print buffer content line by line
    int rows_drawn = 0;
    const char *p = buffer;

    while (*p && rows_drawn < 18)
    {
        const char *next = strchr(p, '\n');
        if (next)
        {
            write(STDOUT_FILENO, p, (size_t)(next - p));
            write(STDOUT_FILENO, "\r\n", 2);
            p = next + 1;
        }
        else
        {
            write(STDOUT_FILENO, p, strlen(p));
            write(STDOUT_FILENO, "\r\n", 2);
            break;
        }
        rows_drawn++;
    }

    // Classic vi empty lines marked with ~
    while (rows_drawn < 18)
    {
        write(STDOUT_FILENO, "~\r\n", 3);
        rows_drawn++;
    }

    // Status bar at bottom
    char status_bar[256];
    if (status_msg && status_msg[0] != '\0')
    {
        snprintf(status_bar, sizeof(status_bar), "\033[7m%s\033[0m\r\n", status_msg);
    }
    else if (mode == 1)
    {
        snprintf(status_bar, sizeof(status_bar), "\033[7m-- INSERT -- (%s)\033[0m\r\n", filename);
    }
    else
    {
        snprintf(status_bar, sizeof(status_bar), "\033[7m\"%s\" [Modified] (Type :wq to save/quit, :q! to discard)\033[0m\r\n", filename);
    }

    write(STDOUT_FILENO, status_bar, strlen(status_bar));
}

// Fallback for non-interactive / piped environments
static void run_non_interactive_editor(char *content, size_t capacity, const char *filename)
{
    char buffer[MAX_BUFFER];
    char line[256];
    int mode = 0; // 0 = NORMAL, 1 = INSERT

    snprintf(buffer, sizeof(buffer), "%s", content);

    while (fgets(line, sizeof(line), stdin) != NULL)
    {
        line[strcspn(line, "\r\n")] = '\0';

        if (mode == 0)
        {
            if (strcmp(line, "i") == 0)
            {
                mode = 1;
            }
            else if (strcmp(line, ":w") == 0)
            {
                snprintf(content, capacity, "%s", buffer);
            }
            else if (strcmp(line, ":q") == 0)
            {
                break;
            }
            else if (strcmp(line, ":wq") == 0)
            {
                snprintf(content, capacity, "%s", buffer);
                break;
            }
            else if (strcmp(line, ":q!") == 0)
            {
                break;
            }
        }
        else
        {
            if (strcmp(line, "ESC") == 0 || strcmp(line, "\x1b") == 0)
            {
                mode = 0;
            }
            else
            {
                size_t cur = strlen(buffer);
                size_t add = strlen(line);
                if (cur + add + 2 < sizeof(buffer))
                {
                    memcpy(buffer + cur, line, add);
                    cur += add;
                    buffer[cur++] = '\n';
                    buffer[cur] = '\0';
                }
            }
        }
    }
    (void)filename;
}

void open_editor(char *content, size_t capacity, const char *filename)
{
    if (!isatty(STDIN_FILENO))
    {
        run_non_interactive_editor(content, capacity, filename);
        return;
    }

    char buffer[MAX_BUFFER];
    snprintf(buffer, sizeof(buffer), "%s", content);

    enable_raw_mode();

    int mode = 0; // 0 = NORMAL, 1 = INSERT, 2 = COMMAND (after ':')
    char cmd_buf[64] = {0};
    int cmd_idx = 0;
    char status_msg[128] = {0};

    render_screen(filename, buffer, mode, NULL);

    char c;
    while (read(STDIN_FILENO, &c, 1) == 1)
    {
        status_msg[0] = '\0';

        // Escape key: 27 (\x1b)
        if (c == 27)
        {
            mode = 0;
            cmd_idx = 0;
            cmd_buf[0] = '\0';
            render_screen(filename, buffer, mode, NULL);
            continue;
        }

        // NORMAL MODE
        if (mode == 0)
        {
            if (c == 'i')
            {
                mode = 1;
                render_screen(filename, buffer, mode, NULL);
            }
            else if (c == ':')
            {
                mode = 2;
                cmd_idx = 0;
                cmd_buf[cmd_idx++] = ':';
                cmd_buf[cmd_idx] = '\0';
                render_screen(filename, buffer, mode, cmd_buf);
            }
            else
            {
                render_screen(filename, buffer, mode, NULL);
            }
        }
        // INSERT MODE
        else if (mode == 1)
        {
            if (c == 127 || c == '\b') // Backspace
            {
                size_t len = strlen(buffer);
                if (len > 0)
                {
                    buffer[len - 1] = '\0';
                }
            }
            else if (c == '\r' || c == '\n') // Enter
            {
                size_t len = strlen(buffer);
                if (len + 2 < sizeof(buffer))
                {
                    buffer[len] = '\n';
                    buffer[len + 1] = '\0';
                }
            }
            else if (c >= 32 && c <= 126) // Printable character
            {
                size_t len = strlen(buffer);
                if (len + 2 < sizeof(buffer))
                {
                    buffer[len] = c;
                    buffer[len + 1] = '\0';
                }
            }
            render_screen(filename, buffer, mode, NULL);
        }
        // COMMAND / EX MODE (after ':')
        else if (mode == 2)
        {
            if (c == '\r' || c == '\n')
            {
                if (strcmp(cmd_buf, ":w") == 0)
                {
                    snprintf(content, capacity, "%s", buffer);
                    snprintf(status_msg, sizeof(status_msg), "\"%s\" written", filename);
                    mode = 0;
                    render_screen(filename, buffer, mode, status_msg);
                }
                else if (strcmp(cmd_buf, ":q") == 0)
                {
                    break;
                }
                else if (strcmp(cmd_buf, ":wq") == 0)
                {
                    snprintf(content, capacity, "%s", buffer);
                    break;
                }
                else if (strcmp(cmd_buf, ":q!") == 0)
                {
                    break;
                }
                else
                {
                    snprintf(status_msg, sizeof(status_msg), "E492: Not an editor command: %s", cmd_buf + 1);
                    mode = 0;
                    render_screen(filename, buffer, mode, status_msg);
                }
                cmd_idx = 0;
                cmd_buf[0] = '\0';
            }
            else if (c == 127 || c == '\b')
            {
                if (cmd_idx > 1)
                {
                    cmd_buf[--cmd_idx] = '\0';
                    render_screen(filename, buffer, mode, cmd_buf);
                }
                else
                {
                    mode = 0;
                    render_screen(filename, buffer, mode, NULL);
                }
            }
            else if (cmd_idx < (int)sizeof(cmd_buf) - 1)
            {
                cmd_buf[cmd_idx++] = c;
                cmd_buf[cmd_idx] = '\0';
                render_screen(filename, buffer, mode, cmd_buf);
            }
        }
    }

    disable_raw_mode();
    // Clear screen on exit and leave cursor ready for shell
    write(STDOUT_FILENO, "\033[2J\033[H", 7);
}
