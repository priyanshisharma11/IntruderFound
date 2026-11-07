#ifndef SIGNALS_H
#define SIGNALS_H

#include <signal.h>

int setup_signal_handlers(void);

int consume_pending_signal(void);

const char *signal_description(int signal_number);

#endif

