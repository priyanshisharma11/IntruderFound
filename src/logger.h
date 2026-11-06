#ifndef LOGGER_H
#define LOGGER_H

void logger_start(void);
void logger_log(const char *event, const char *details);
void logger_end(void);

#endif

