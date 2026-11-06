#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "logger.h"

FILE *log_file = NULL;

char session_id[64];


// Generate current timestamp
void get_timestamp(char timestamp[])
{
    time_t current_time = time(NULL);

    struct tm *time_info = localtime(&current_time);

    strftime(timestamp, 32, "%Y-%m-%d %H:%M:%S", time_info);
}


// Start a new session
void logger_start(void)
{
    char timestamp[32];

    log_file = fopen("logs/session.log", "a");

    if (log_file == NULL)
    {
        perror("Unable to open session log");
        return;
    }

    get_timestamp(timestamp);

    // Generate unique session ID using time and process ID
    snprintf(session_id, sizeof(session_id),
             "%s_%ld", timestamp, (long)getpid());

    fprintf(log_file,
            "%s|%s|SESSION_START|Decoy shell started\n",
            timestamp, session_id);

    fflush(log_file);
}


// Record an event
void logger_log(const char *event, const char *details)
{
    char timestamp[32];
    char safe_details[512];

    if (log_file == NULL)
    {
        return;
    }

    get_timestamp(timestamp);

    snprintf(safe_details, sizeof(safe_details), "%s", details);

    // Prevent log-field injection using separators or newlines
    for (int i = 0; safe_details[i] != '\0'; i++)
    {
        if (safe_details[i] == '|' ||
            safe_details[i] == '\n' ||
            safe_details[i] == '\r')
        {
            safe_details[i] = ' ';
        }
    }

    fprintf(log_file, "%s|%s|%s|%s\n",
            timestamp, session_id, event, safe_details);

    fflush(log_file);
}


// End the session
void logger_end(void)
{
    if (log_file == NULL)
    {
        return;
    }

    char timestamp[32];

    get_timestamp(timestamp);

    fprintf(log_file,
            "%s|%s|SESSION_END|Decoy shell closed\n",
            timestamp, session_id);

    fclose(log_file);

    log_file = NULL;
}

