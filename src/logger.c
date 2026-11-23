#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <libgen.h>
#include <sys/stat.h>
#include <sys/types.h>

#if defined(__APPLE__)
#include <mach-o/dyld.h>
#endif

#include "logger.h"

static int log_fd = -1;
static char session_id[64];

// Resolve absolute path to <project_dir>/logs/session.log relative to the binary
static void get_log_file_path(char *path_out, size_t size)
{
    char exe_path[1024] = {0};
    int found = 0;

#if defined(__APPLE__)
    uint32_t buf_size = sizeof(exe_path);
    if (_NSGetExecutablePath(exe_path, &buf_size) == 0)
    {
        found = 1;
    }
#elif defined(__linux__)
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len != -1)
    {
        exe_path[len] = '\0';
        found = 1;
    }
#endif

    if (found)
    {
        char *dir = dirname(exe_path);
        char log_dir[1024];
        snprintf(log_dir, sizeof(log_dir), "%s/logs", dir);
        mkdir(log_dir, 0755);
        snprintf(path_out, size, "%s/logs/session.log", dir);
    }
    else
    {
        mkdir("logs", 0755);
        snprintf(path_out, size, "logs/session.log");
    }
}

// Generate current timestamp (ISO-like: YYYY-MM-DD HH:MM:SS)
static void get_timestamp(char timestamp[], size_t size)
{
    time_t current_time = time(NULL);
    struct tm *time_info = localtime(&current_time);
    strftime(timestamp, size, "%Y-%m-%d %H:%M:%S", time_info);
}

// Start a new session using low-level POSIX file descriptors
void logger_start(void)
{
    char timestamp[32];
    char entry[256];
    char log_path[1024];

    get_log_file_path(log_path, sizeof(log_path));

    // POSIX open: append-only, create if not present
    log_fd = open(log_path, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (log_fd == -1)
    {
        perror("logger: open(session.log) failed");
        return;
    }

    get_timestamp(timestamp, sizeof(timestamp));

    // Unique session ID: YYYYMMDD_HHMMSS_PID (no spaces)
    char ts_nospace[32];
    size_t k = 0;
    for (size_t j = 0; timestamp[j] != '\0' && k < sizeof(ts_nospace) - 1; j++)
    {
        if (timestamp[j] == ' ' || timestamp[j] == '-' || timestamp[j] == ':')
        {
            ts_nospace[k++] = '_';
        }
        else
        {
            ts_nospace[k++] = timestamp[j];
        }
    }
    ts_nospace[k] = '\0';

    snprintf(session_id, sizeof(session_id), "%s_%ld", ts_nospace, (long)getpid());

    int len = snprintf(entry, sizeof(entry), "%s|%s|SESSION_START|Decoy shell started\n",
                       timestamp, session_id);
    if (len > 0)
    {
        write(log_fd, entry, (size_t)len);
        fsync(log_fd);
    }
}

// Record an event to the append-only log using POSIX write()
void logger_log(const char *event, const char *details)
{
    char timestamp[32];
    char safe_details[512];
    char entry[1024];

    if (log_fd == -1)
    {
        return;
    }

    get_timestamp(timestamp, sizeof(timestamp));

    // Sanitize log details to prevent delimiter injection
    size_t i = 0;
    while (details[i] != '\0' && i < sizeof(safe_details) - 1)
    {
        char c = details[i];
        if (c == '|' || c == '\n' || c == '\r')
        {
            safe_details[i] = ' ';
        }
        else
        {
            safe_details[i] = c;
        }
        i++;
    }
    safe_details[i] = '\0';

    int len = snprintf(entry, sizeof(entry), "%s|%s|%s|%s\n",
                       timestamp, session_id, event, safe_details);
    if (len > 0)
    {
        write(log_fd, entry, (size_t)len);
        fsync(log_fd);
    }
}

// End the session and close the file descriptor
void logger_end(void)
{
    if (log_fd == -1)
    {
        return;
    }

    char timestamp[32];
    char entry[256];

    get_timestamp(timestamp, sizeof(timestamp));

    int len = snprintf(entry, sizeof(entry), "%s|%s|SESSION_END|Decoy shell closed\n",
                       timestamp, session_id);
    if (len > 0)
    {
        write(log_fd, entry, (size_t)len);
        fsync(log_fd);
    }

    close(log_fd);
    log_fd = -1;
}
