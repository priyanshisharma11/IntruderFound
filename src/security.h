#ifndef SECURITY_H
#define SECURITY_H

#include <stddef.h>

typedef struct {
    int is_suspicious;
    const char *category;
    char simulated_output[512];
    int prompt_password;
} SecurityResult;

SecurityResult evaluate_security(const char *raw_input);

#endif
