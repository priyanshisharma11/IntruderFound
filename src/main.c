#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <termios.h>
#include <sys/stat.h>

#include "editor.h"
#include "logger.h"
#include "security.h"
#include "signals.h"

#define DECOY_USER "user123"
#define DECOY_HOSTNAME "srv-node01"

// Simulated Inode Structure (Module 3 & Riddhi's Work Division)
typedef struct Inode {
    int ino;
    int is_directory;
    mode_t mode;        // POSIX permissions (e.g. 0755, 0644)
    char owner[32];     // e.g. DECOY_USER
    char group[32];     // e.g. DECOY_USER
    size_t size;
    time_t mtime;
    char content[1024]; // in-memory file content
} Inode;

// Virtual Directory Tree Node
typedef struct Node {
    char name[64];
    Inode *inode;
    struct Node *parent;
    struct Node *children;
    struct Node *next;
} Node;

static int next_inode_number = 1000;

static Inode *create_inode(int is_directory, mode_t mode, const char *owner, const char *group)
{
    Inode *ino = malloc(sizeof(Inode));
    if (!ino)
    {
        perror("malloc inode failed");
        exit(1);
    }
    ino->ino = next_inode_number++;
    ino->is_directory = is_directory;
    ino->mode = mode;
    strncpy(ino->owner, owner, sizeof(ino->owner) - 1);
    ino->owner[sizeof(ino->owner) - 1] = '\0';
    strncpy(ino->group, group, sizeof(ino->group) - 1);
    ino->group[sizeof(ino->group) - 1] = '\0';
    ino->size = is_directory ? 4096 : 0;
    ino->mtime = time(NULL);
    ino->content[0] = '\0';
    return ino;
}

static Node *create_node(const char *name, int is_directory, mode_t mode, const char *owner, const char *group)
{
    Node *node = malloc(sizeof(Node));
    if (!node)
    {
        perror("malloc node failed");
        exit(1);
    }
    strncpy(node->name, name, sizeof(node->name) - 1);
    node->name[sizeof(node->name) - 1] = '\0';
    node->inode = create_inode(is_directory, mode, owner, group);
    node->parent = NULL;
    node->children = NULL;
    node->next = NULL;
    return node;
}

static void add_child(Node *parent, Node *child)
{
    child->parent = parent;
    if (parent->children == NULL)
    {
        parent->children = child;
    }
    else
    {
        Node *temp = parent->children;
        while (temp->next != NULL)
        {
            temp = temp->next;
        }
        temp->next = child;
    }
}

static Node *find_child(Node *directory, const char *name)
{
    Node *temp = directory->children;
    while (temp != NULL)
    {
        if (strcmp(temp->name, name) == 0)
        {
            return temp;
        }
        temp = temp->next;
    }
    return NULL;
}

static int remove_child(Node *parent, const char *name)
{
    Node *cur = parent->children;
    Node *prev = NULL;

    while (cur != NULL)
    {
        if (strcmp(cur->name, name) == 0)
        {
            if (prev == NULL)
            {
                parent->children = cur->next;
            }
            else
            {
                prev->next = cur->next;
            }
            if (cur->inode)
            {
                free(cur->inode);
            }
            free(cur);
            return 1;
        }
        prev = cur;
        cur = cur->next;
    }
    return 0;
}

static void get_full_path(Node *node, char *buffer, size_t size)
{
    if (node->parent == NULL)
    {
        snprintf(buffer, size, "/");
        return;
    }
    if (node->parent->parent == NULL)
    {
        snprintf(buffer, size, "/%s", node->name);
        return;
    }
    char parent_buf[256];
    get_full_path(node->parent, parent_buf, sizeof(parent_buf));
    if (strcmp(parent_buf, "/") == 0)
    {
        snprintf(buffer, size, "/%s", node->name);
    }
    else
    {
        snprintf(buffer, size, "%s/%s", parent_buf, node->name);
    }
}

// Multi-level Path Resolution (supports absolute, relative, '.', '..', and '~')
static Node *resolve_path(Node *current, Node *root, Node *home, const char *path)
{
    if (path == NULL || path[0] == '\0' || strcmp(path, ".") == 0)
    {
        return current;
    }

    Node *curr = current;
    char path_copy[256];
    strncpy(path_copy, path, sizeof(path_copy) - 1);
    path_copy[sizeof(path_copy) - 1] = '\0';

    char *p = path_copy;

    if (p[0] == '/')
    {
        curr = root;
        p++;
    }
    else if (p[0] == '~')
    {
        curr = home;
        p++;
        if (p[0] == '/')
        {
            p++;
        }
    }

    char *token = strtok(p, "/");
    while (token != NULL)
    {
        if (strcmp(token, ".") == 0)
        {
            // no-op
        }
        else if (strcmp(token, "..") == 0)
        {
            if (curr->parent != NULL)
            {
                curr = curr->parent;
            }
        }
        else
        {
            Node *next_node = find_child(curr, token);
            if (next_node == NULL)
            {
                return NULL;
            }
            curr = next_node;
        }
        token = strtok(NULL, "/");
    }

    return curr;
}

// Format mode_t to string (e.g. drwxr-xr-x)
static void format_mode(mode_t mode, int is_dir, char str[11])
{
    str[0] = is_dir ? 'd' : '-';
    str[1] = (mode & 0400) ? 'r' : '-';
    str[2] = (mode & 0200) ? 'w' : '-';
    str[3] = (mode & 0100) ? 'x' : '-';
    str[4] = (mode & 0040) ? 'r' : '-';
    str[5] = (mode & 0020) ? 'w' : '-';
    str[6] = (mode & 0010) ? 'x' : '-';
    str[7] = (mode & 0004) ? 'r' : '-';
    str[8] = (mode & 0002) ? 'w' : '-';
    str[9] = (mode & 0001) ? 'x' : '-';
    str[10] = '\0';
}

static void list_directory(Node *dir, int long_format, int show_hidden)
{
    Node *temp = dir->children;

    if (temp == NULL && !long_format)
    {
        return;
    }

    if (long_format)
    {
        // Calculate total 1K blocks simulated
        int total_blocks = 0;
        Node *scan = dir->children;
        while (scan != NULL)
        {
            total_blocks += scan->inode->is_directory ? 4 : 1;
            scan = scan->next;
        }
        printf("total %d\n", total_blocks);
    }

    while (temp != NULL)
    {
        if (!show_hidden && temp->name[0] == '.')
        {
            temp = temp->next;
            continue;
        }

        if (long_format)
        {
            char modestr[11];
            format_mode(temp->inode->mode, temp->inode->is_directory, modestr);

            char date_str[32];
            struct tm *tm_info = localtime(&temp->inode->mtime);
            strftime(date_str, sizeof(date_str), "%b %e %H:%M", tm_info);

            printf("%s 1 %-8s %-8s %6zu %s %s%s\n",
                   modestr,
                   temp->inode->owner,
                   temp->inode->group,
                   temp->inode->size,
                   date_str,
                   temp->name,
                   temp->inode->is_directory ? "/" : "");
        }
        else
        {
            printf("%s%s  ", temp->name, temp->inode->is_directory ? "/" : "");
        }
        temp = temp->next;
    }

    if (!long_format)
    {
        printf("\n");
    }
}

static void trim_spaces(char text[])
{
    int start = 0;
    int end = (int)strlen(text) - 1;

    while (text[start] == ' ' || text[start] == '\t')
    {
        start++;
    }

    while (end >= start && (text[end] == ' ' || text[end] == '\t'))
    {
        text[end] = '\0';
        end--;
    }

    if (start > 0)
    {
        memmove(text, text + start, strlen(text + start) + 1);
    }
}

// Simulated echo and redirection (bounds-checked)
static void process_echo(Node *current_dir, Node *root, Node *home, const char *input)
{
    char text[512];
    char target_path[128];
    const char *content_start = input + 4;

    while (*content_start == ' ')
    {
        content_start++;
    }

    const char *redir_append = strstr(content_start, ">>");
    const char *redir_overwrite = strchr(content_start, '>');
    int append = 0;
    const char *redir_pos = NULL;

    if (redir_append != NULL)
    {
        append = 1;
        redir_pos = redir_append;
    }
    else if (redir_overwrite != NULL)
    {
        append = 0;
        redir_pos = redir_overwrite;
    }

    if (redir_pos == NULL)
    {
        snprintf(text, sizeof(text), "%s", content_start);
        trim_spaces(text);
        size_t len = strlen(text);
        if (len >= 2 && text[0] == '"' && text[len - 1] == '"')
        {
            memmove(text, text + 1, len - 2);
            text[len - 2] = '\0';
        }
        printf("%s\n", text);
        return;
    }

    // Extract text before redirection
    size_t text_len = (size_t)(redir_pos - content_start);
    if (text_len >= sizeof(text))
    {
        text_len = sizeof(text) - 1;
    }
    strncpy(text, content_start, text_len);
    text[text_len] = '\0';
    trim_spaces(text);

    size_t len = strlen(text);
    if (len >= 2 && text[0] == '"' && text[len - 1] == '"')
    {
        memmove(text, text + 1, len - 2);
        text[len - 2] = '\0';
    }

    // Extract destination path
    const char *path_start = redir_pos + (append ? 2 : 1);
    while (*path_start == ' ')
    {
        path_start++;
    }

    if (sscanf(path_start, "%127s", target_path) != 1)
    {
        printf("bash: syntax error near unexpected token 'newline'\n");
        return;
    }

    // Locate parent and filename
    char dir_part[128] = ".";
    char file_part[64];
    char *last_slash = strrchr(target_path, '/');
    if (last_slash)
    {
        size_t dlen = (size_t)(last_slash - target_path);
        if (dlen == 0)
        {
            strcpy(dir_part, "/");
        }
        else
        {
            strncpy(dir_part, target_path, dlen);
            dir_part[dlen] = '\0';
        }
        strncpy(file_part, last_slash + 1, sizeof(file_part) - 1);
        file_part[sizeof(file_part) - 1] = '\0';
    }
    else
    {
        strncpy(file_part, target_path, sizeof(file_part) - 1);
        file_part[sizeof(file_part) - 1] = '\0';
    }

    Node *dest_dir = resolve_path(current_dir, root, home, dir_part);
    if (!dest_dir || !dest_dir->inode->is_directory)
    {
        printf("bash: %s: No such file or directory\n", target_path);
        return;
    }

    Node *file = find_child(dest_dir, file_part);
    if (file != NULL && file->inode->is_directory)
    {
        printf("bash: %s: Is a directory\n", target_path);
        return;
    }

    if (file == NULL)
    {
        file = create_node(file_part, 0, 0644, DECOY_USER, DECOY_USER);
        add_child(dest_dir, file);
    }

    size_t cur_len = strlen(file->inode->content);
    size_t add_len = strlen(text);

    if (append)
    {
        if (cur_len + add_len + 2 >= sizeof(file->inode->content))
        {
            printf("bash: %s: No space left on device\n", target_path);
            return;
        }
        strcat(file->inode->content, text);
        strcat(file->inode->content, "\n");
    }
    else
    {
        if (add_len + 2 >= sizeof(file->inode->content))
        {
            printf("bash: %s: File too large\n", target_path);
            return;
        }
        strcpy(file->inode->content, text);
        strcat(file->inode->content, "\n");
    }

    file->inode->size = strlen(file->inode->content);
    file->inode->mtime = time(NULL);
}

// Fake password prompt for sudo/passwd without echoing password
static void fake_password_prompt(const char *prompt)
{
    printf("%s", prompt);
    fflush(stdout);

    struct termios oldt, newt;
    int is_term = isatty(STDIN_FILENO);

    if (is_term)
    {
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    }

    char dummy[128];
    if (fgets(dummy, sizeof(dummy), stdin) == NULL)
    {
        // EOF
    }

    if (is_term)
    {
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    }
    printf("\n");
}

int main(void)
{
    // Build simulated file system hierarchy with Inode attributes
    Node *root = create_node("", 1, 0755, "root", "root");
    Node *home = create_node("home", 1, 0755, "root", "root");
    Node *user = create_node(DECOY_USER, 1, 0755, DECOY_USER, DECOY_USER);

    add_child(root, home);
    add_child(home, user);

    Node *current_dir = user;

    Node *documents = create_node("Documents", 1, 0755, DECOY_USER, DECOY_USER);
    Node *downloads = create_node("Downloads", 1, 0755, DECOY_USER, DECOY_USER);
    add_child(user, documents);
    add_child(user, downloads);

    Node *secrets = create_node("secrets.txt", 0, 0600, DECOY_USER, DECOY_USER);
    strcpy(secrets->inode->content, "CONFIDENTIAL: API_KEY=c3VwZXJfc2VjcmV0X3Rva2Vu\n");
    secrets->inode->size = strlen(secrets->inode->content);
    add_child(user, secrets);

    Node *notes = create_node("notes.txt", 0, 0644, DECOY_USER, DECOY_USER);
    strcpy(notes->inode->content, "Review UNIX process control and signal handling.\n");
    notes->inode->size = strlen(notes->inode->content);
    add_child(documents, notes);

    Node *assignment = create_node("assignment.txt", 0, 0644, DECOY_USER, DECOY_USER);
    strcpy(assignment->inode->content, "Course Code: 24B15CS214 - UNIX Programming Lab\n");
    assignment->inode->size = strlen(assignment->inode->content);
    add_child(documents, assignment);

    Node *report = create_node("report.pdf", 0, 0644, DECOY_USER, DECOY_USER);
    strcpy(report->inode->content, "%PDF-1.4 simulated pdf stream\n");
    report->inode->size = strlen(report->inode->content);
    add_child(downloads, report);

    logger_start();

    if (setup_signal_handlers() == -1)
    {
        logger_end();
        return 1;
    }

    char cwd_path[256];
    char input[512];
    char command[64];
    char arg1[128];
    char arg2[128];

    while (1)
    {
        get_full_path(current_dir, cwd_path, sizeof(cwd_path));

        // Format prompt: user123@srv-node01:~$ or user123@srv-node01:/path$
        if (current_dir == user)
        {
            printf("%s@%s:~$ ", DECOY_USER, DECOY_HOSTNAME);
        }
        else
        {
            printf("%s@%s:%s$ ", DECOY_USER, DECOY_HOSTNAME, cwd_path);
        }
        fflush(stdout);

        if (fgets(input, sizeof(input), stdin) == NULL)
        {
            int sig = consume_pending_signal();
            if (sig == SIGINT)
            {
                logger_log("SIGNAL", "SIGINT intercepted (^C)");
                printf("^C\n");
                clearerr(stdin);
                continue;
            }
            else if (sig == SIGTSTP)
            {
                logger_log("SIGNAL", "SIGTSTP intercepted (^Z)");
                printf("\n");
                clearerr(stdin);
                continue;
            }
            else if (sig == SIGHUP)
            {
                logger_log("SIGNAL", "SIGHUP received (Hangup)");
                logger_end();
                break;
            }

            logger_end();
            printf("exit\n");
            break;
        }

        // Check if an asynchronous signal was received during input
        int sig = consume_pending_signal();
        if (sig == SIGINT)
        {
            logger_log("SIGNAL", "SIGINT intercepted (^C)");
            printf("^C\n");
            continue;
        }
        else if (sig == SIGTSTP)
        {
            logger_log("SIGNAL", "SIGTSTP intercepted (^Z)");
            printf("\n");
            continue;
        }
        else if (sig == SIGHUP)
        {
            logger_log("SIGNAL", "SIGHUP received (Hangup)");
            logger_end();
            break;
        }

        input[strcspn(input, "\r\n")] = '\0';
        trim_spaces(input);

        if (input[0] == '\0')
        {
            continue;
        }

        logger_log("COMMAND", input);

        // Security Evaluation: Honeypot Deception Logic
        SecurityResult sec = evaluate_security(input);
        if (sec.is_suspicious)
        {
            logger_log("SUSPICIOUS", sec.category);

            if (sec.prompt_password)
            {
                if (strncmp(input, "sudo", 4) == 0)
                {
                    char prompt[128];
                    snprintf(prompt, sizeof(prompt), "[sudo] password for %s: ", DECOY_USER);
                    fake_password_prompt(prompt);
                }
                else if (strncmp(input, "su", 2) == 0)
                {
                    fake_password_prompt("Password: ");
                }
                else if (strncmp(input, "passwd", 6) == 0)
                {
                    printf("Changing password for %s.\n", DECOY_USER);
                    fake_password_prompt("(current) UNIX password: ");
                }
            }

            // Print simulated authentic UNIX response (No "Security alert" giveaway!)
            printf("%s", sec.simulated_output);
            continue;
        }

        command[0] = '\0';
        arg1[0] = '\0';
        arg2[0] = '\0';

        sscanf(input, "%63s %127s %127s", command, arg1, arg2);

        if (strcmp(command, "exit") == 0)
        {
            logger_end();
            printf("logout\n");
            break;
        }
        else if (strcmp(command, "help") == 0)
        {
            printf("IntruderFound Shell (POSIX Emulation)\n");
            printf("Available built-in commands:\n");
            printf("  ls [-l|-la] [path]  List directory contents\n");
            printf("  cd [path]           Change working directory\n");
            printf("  pwd                 Print current working directory\n");
            printf("  cat [file]          Display file contents\n");
            printf("  echo [text] [> file]Print text or redirect to file\n");
            printf("  touch [file]        Create an empty file\n");
            printf("  mkdir [dir]         Create directory\n");
            printf("  rm [file]           Remove file\n");
            printf("  cp [src] [dst]      Copy file\n");
            printf("  mv [src] [dst]      Move or rename file\n");
            printf("  vi [file]           Simulated modal text editor\n");
            printf("  whoami, id          User identity\n");
            printf("  uname [-a]          System information\n");
            printf("  exit                Terminate session\n");
        }
        else if (strcmp(command, "pwd") == 0)
        {
            printf("%s\n", cwd_path);
        }
        else if (strcmp(command, "whoami") == 0)
        {
            printf("%s\n", DECOY_USER);
        }
        else if (strcmp(command, "id") == 0)
        {
            printf("uid=1001(%s) gid=1001(%s) groups=1001(%s)\n", DECOY_USER, DECOY_USER, DECOY_USER);
        }
        else if (strcmp(command, "uname") == 0)
        {
            if (strcmp(arg1, "-a") == 0)
            {
                printf("Linux %s 5.15.0-89-generic #99-Ubuntu SMP Mon Oct 30 20:42:41 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux\n", DECOY_HOSTNAME);
            }
            else
            {
                printf("Linux\n");
            }
        }
        else if (strcmp(command, "cd") == 0)
        {
            const char *target = (arg1[0] == '\0') ? "~" : arg1;
            Node *dest = resolve_path(current_dir, root, user, target);

            if (dest == NULL)
            {
                printf("bash: cd: %s: No such file or directory\n", target);
            }
            else if (!dest->inode->is_directory)
            {
                printf("bash: cd: %s: Not a directory\n", target);
            }
            else
            {
                current_dir = dest;
            }
        }
        else if (strcmp(command, "ls") == 0)
        {
            int long_fmt = 0;
            int show_all = 0;
            const char *path_arg = NULL;

            if (arg1[0] == '-')
            {
                if (strstr(arg1, "l")) long_fmt = 1;
                if (strstr(arg1, "a")) show_all = 1;
                path_arg = (arg2[0] != '\0') ? arg2 : NULL;
            }
            else if (arg1[0] != '\0')
            {
                path_arg = arg1;
            }

            Node *target_dir = current_dir;
            if (path_arg)
            {
                target_dir = resolve_path(current_dir, root, user, path_arg);
            }

            if (target_dir == NULL)
            {
                printf("ls: cannot access '%s': No such file or directory\n", path_arg);
            }
            else if (!target_dir->inode->is_directory)
            {
                printf("%s\n", target_dir->name);
            }
            else
            {
                list_directory(target_dir, long_fmt, show_all);
            }
        }
        else if (strcmp(command, "cat") == 0)
        {
            if (arg1[0] == '\0')
            {
                continue;
            }

            Node *target = resolve_path(current_dir, root, user, arg1);
            if (target == NULL)
            {
                printf("cat: %s: No such file or directory\n", arg1);
            }
            else if (target->inode->is_directory)
            {
                printf("cat: %s: Is a directory\n", arg1);
            }
            else
            {
                printf("%s", target->inode->content);
                size_t clen = strlen(target->inode->content);
                if (clen > 0 && target->inode->content[clen - 1] != '\n')
                {
                    printf("\n");
                }
            }
        }
        else if (strcmp(command, "touch") == 0)
        {
            if (arg1[0] == '\0')
            {
                printf("touch: missing file operand\n");
                continue;
            }

            char dir_part[128] = ".";
            char file_part[64];
            char *slash = strrchr(arg1, '/');
            if (slash)
            {
                size_t dlen = (size_t)(slash - arg1);
                if (dlen == 0) strcpy(dir_part, "/");
                else { strncpy(dir_part, arg1, dlen); dir_part[dlen] = '\0'; }
                strncpy(file_part, slash + 1, sizeof(file_part) - 1);
                file_part[sizeof(file_part) - 1] = '\0';
            }
            else
            {
                strncpy(file_part, arg1, sizeof(file_part) - 1);
                file_part[sizeof(file_part) - 1] = '\0';
            }

            Node *pdir = resolve_path(current_dir, root, user, dir_part);
            if (!pdir || !pdir->inode->is_directory)
            {
                printf("touch: cannot touch '%s': No such file or directory\n", arg1);
            }
            else
            {
                Node *existing = find_child(pdir, file_part);
                if (existing)
                {
                    existing->inode->mtime = time(NULL);
                }
                else
                {
                    Node *new_f = create_node(file_part, 0, 0644, DECOY_USER, DECOY_USER);
                    add_child(pdir, new_f);
                }
            }
        }
        else if (strcmp(command, "mkdir") == 0)
        {
            if (arg1[0] == '\0')
            {
                printf("mkdir: missing operand\n");
                continue;
            }

            char dir_part[128] = ".";
            char name_part[64];
            char *slash = strrchr(arg1, '/');
            if (slash)
            {
                size_t dlen = (size_t)(slash - arg1);
                if (dlen == 0) strcpy(dir_part, "/");
                else { strncpy(dir_part, arg1, dlen); dir_part[dlen] = '\0'; }
                strncpy(name_part, slash + 1, sizeof(name_part) - 1);
                name_part[sizeof(name_part) - 1] = '\0';
            }
            else
            {
                strncpy(name_part, arg1, sizeof(name_part) - 1);
                name_part[sizeof(name_part) - 1] = '\0';
            }

            Node *pdir = resolve_path(current_dir, root, user, dir_part);
            if (!pdir || !pdir->inode->is_directory)
            {
                printf("mkdir: cannot create directory '%s': No such file or directory\n", arg1);
            }
            else if (find_child(pdir, name_part) != NULL)
            {
                printf("mkdir: cannot create directory '%s': File exists\n", arg1);
            }
            else
            {
                Node *new_d = create_node(name_part, 1, 0755, DECOY_USER, DECOY_USER);
                add_child(pdir, new_d);
            }
        }
        else if (strcmp(command, "rm") == 0)
        {
            if (arg1[0] == '\0')
            {
                printf("rm: missing operand\n");
                continue;
            }

            char dir_part[128] = ".";
            char file_part[64];
            char *slash = strrchr(arg1, '/');
            if (slash)
            {
                size_t dlen = (size_t)(slash - arg1);
                if (dlen == 0) strcpy(dir_part, "/");
                else { strncpy(dir_part, arg1, dlen); dir_part[dlen] = '\0'; }
                strncpy(file_part, slash + 1, sizeof(file_part) - 1);
                file_part[sizeof(file_part) - 1] = '\0';
            }
            else
            {
                strncpy(file_part, arg1, sizeof(file_part) - 1);
                file_part[sizeof(file_part) - 1] = '\0';
            }

            Node *pdir = resolve_path(current_dir, root, user, dir_part);
            if (!pdir)
            {
                printf("rm: cannot remove '%s': No such file or directory\n", arg1);
            }
            else
            {
                Node *target = find_child(pdir, file_part);
                if (!target)
                {
                    printf("rm: cannot remove '%s': No such file or directory\n", arg1);
                }
                else if (target->inode->is_directory)
                {
                    printf("rm: cannot remove '%s': Is a directory\n", arg1);
                }
                else
                {
                    remove_child(pdir, file_part);
                }
            }
        }
        else if (strcmp(command, "cp") == 0)
        {
            if (arg1[0] == '\0' || arg2[0] == '\0')
            {
                printf("cp: missing file operand\n");
                continue;
            }

            Node *src = resolve_path(current_dir, root, user, arg1);
            if (!src || src->inode->is_directory)
            {
                printf("cp: cannot stat '%s': No such file or directory\n", arg1);
                continue;
            }

            Node *dst = resolve_path(current_dir, root, user, arg2);
            if (dst && dst->inode->is_directory)
            {
                Node *copy = create_node(src->name, 0, src->inode->mode, DECOY_USER, DECOY_USER);
                strcpy(copy->inode->content, src->inode->content);
                copy->inode->size = src->inode->size;
                add_child(dst, copy);
            }
            else
            {
                Node *new_f = create_node(arg2, 0, src->inode->mode, DECOY_USER, DECOY_USER);
                strcpy(new_f->inode->content, src->inode->content);
                new_f->inode->size = src->inode->size;
                add_child(current_dir, new_f);
            }
        }
        else if (strcmp(command, "mv") == 0)
        {
            if (arg1[0] == '\0' || arg2[0] == '\0')
            {
                printf("mv: missing file operand\n");
                continue;
            }

            Node *src = resolve_path(current_dir, root, user, arg1);
            if (!src)
            {
                printf("mv: cannot stat '%s': No such file or directory\n", arg1);
                continue;
            }

            Node *dst = resolve_path(current_dir, root, user, arg2);
            if (dst && dst->inode->is_directory)
            {
                remove_child(src->parent, src->name);
                add_child(dst, src);
            }
            else
            {
                strncpy(src->name, arg2, sizeof(src->name) - 1);
                src->name[sizeof(src->name) - 1] = '\0';
            }
        }
        else if (strcmp(command, "echo") == 0)
        {
            process_echo(current_dir, root, user, input);
        }
        else if (strcmp(command, "vi") == 0 || strcmp(command, "vim") == 0)
        {
            if (arg1[0] == '\0')
            {
                printf("vi: missing filename\n");
                continue;
            }

            Node *file = resolve_path(current_dir, root, user, arg1);
            if (file != NULL && file->inode->is_directory)
            {
                printf("vi: %s is a directory\n", arg1);
            }
            else
            {
                if (file == NULL)
                {
                    file = create_node(arg1, 0, 0644, DECOY_USER, DECOY_USER);
                    add_child(current_dir, file);
                }
                open_editor(file->inode->content, sizeof(file->inode->content), file->name);
                file->inode->size = strlen(file->inode->content);
                file->inode->mtime = time(NULL);
            }
        }
        else
        {
            printf("%s: command not found\n", command);
        }
    }

    return 0;
}
