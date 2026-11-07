#include <stdio.h>
#include <signal.h>
#include <string.h>

#include "signals.h"


// Stores the signal received
volatile sig_atomic_t pending_signal = 0;


// Signal handler
void handle_signal(int signal_number)
{
    pending_signal = signal_number;
}


// Install signal handlers
int setup_signal_handlers(void)
{
    struct sigaction action;

    memset(&action, 0, sizeof(action));

    action.sa_handler = handle_signal;

    sigemptyset(&action.sa_mask);

    action.sa_flags = 0;


    if (sigaction(SIGINT, &action, NULL) == -1)
    {
        perror("SIGINT handler installation failed");
        return -1;
    }

    if (sigaction(SIGTSTP, &action, NULL) == -1)
    {
        perror("SIGTSTP handler installation failed");
        return -1;
    }

    if (sigaction(SIGHUP, &action, NULL) == -1)
    {
        perror("SIGHUP handler installation failed");
        return -1;
    }

    return 0;
}


// Read and clear the pending signal
int consume_pending_signal(void)
{
    int received = pending_signal;

    pending_signal = 0;

    return received;
}


// Return signal description
const char *signal_description(int signal_number)
{
    if (signal_number == SIGINT)
    {
        return "SIGINT - Interrupt received";
    }

    if (signal_number == SIGTSTP)
    {
        return "SIGTSTP - Terminal stop requested";
    }

    if (signal_number == SIGHUP)
    {
        return "SIGHUP - Terminal hangup received";
    }

    return "Unknown signal";
}

