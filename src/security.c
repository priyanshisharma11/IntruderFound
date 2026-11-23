#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "security.h"

// Tokenize space-separated arguments safely
static int tokenize(const char *input, char tokens[16][64])
{
    int count = 0;
    const char *p = input;

    while (*p && count < 16)
    {
        while (*p && isspace((unsigned char)*p))
        {
            p++;
        }
        if (!*p)
        {
            break;
        }

        int len = 0;
        while (*p && !isspace((unsigned char)*p) && len < 63)
        {
            tokens[count][len++] = *p++;
        }
        tokens[count][len] = '\0';
        count++;

        while (*p && !isspace((unsigned char)*p))
        {
            p++;
        }
    }
    return count;
}

SecurityResult evaluate_security(const char *raw_input)
{
    SecurityResult res;
    memset(&res, 0, sizeof(res));

    if (raw_input == NULL || raw_input[0] == '\0')
    {
        return res;
    }

    char tokens[16][64];
    int token_count = tokenize(raw_input, tokens);

    if (token_count == 0)
    {
        return res;
    }

    const char *cmd = tokens[0];

    // 1. Privilege escalation: sudo
    if (strcmp(cmd, "sudo") == 0)
    {
        res.is_suspicious = 1;
        res.category = "Privilege escalation attempt (sudo)";
        res.prompt_password = 1;
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "sudo: 3 incorrect password attempts\n");
        return res;
    }

    // 2. Privilege escalation: su
    if (strcmp(cmd, "su") == 0)
    {
        res.is_suspicious = 1;
        res.category = "Privilege escalation attempt (su)";
        res.prompt_password = 1;
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "su: Authentication failure\n");
        return res;
    }

    // 3. File permission modification: chmod
    if (strcmp(cmd, "chmod") == 0)
    {
        res.is_suspicious = 1;
        res.category = "File permission modification (chmod)";
        const char *target = (token_count > 2) ? tokens[2] : (token_count > 1 ? tokens[1] : "file");
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "chmod: changing permissions of '%s': Operation not permitted\n", target);
        return res;
    }

    // 4. File ownership modification: chown / chgrp
    if (strcmp(cmd, "chown") == 0 || strcmp(cmd, "chgrp") == 0)
    {
        res.is_suspicious = 1;
        res.category = "File ownership modification (chown)";
        const char *target = (token_count > 2) ? tokens[2] : (token_count > 1 ? tokens[1] : "file");
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "%s: changing ownership of '%s': Operation not permitted\n", cmd, target);
        return res;
    }

    // 5. Password alteration: passwd
    if (strcmp(cmd, "passwd") == 0)
    {
        res.is_suspicious = 1;
        res.category = "Password modification attempt (passwd)";
        res.prompt_password = 1;
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "passwd: Authentication token manipulation error\npasswd: password unchanged\n");
        return res;
    }

    // 6. Destructive operations: rm -rf, etc.
    if (strcmp(cmd, "rm") == 0)
    {
        int has_recursive = 0;
        int targets_root = 0;

        for (int i = 1; i < token_count; i++)
        {
            if (strstr(tokens[i], "-r") != NULL || strstr(tokens[i], "-R") != NULL)
            {
                has_recursive = 1;
            }
            if (strcmp(tokens[i], "/") == 0 || strcmp(tokens[i], "/*") == 0 ||
                strcmp(tokens[i], "/etc") == 0 || strcmp(tokens[i], "/bin") == 0)
            {
                targets_root = 1;
            }
        }

        if (has_recursive && targets_root)
        {
            res.is_suspicious = 1;
            res.category = "Destructive file operation (rm -rf)";
            snprintf(res.simulated_output, sizeof(res.simulated_output),
                     "rm: it is dangerous to operate recursively on '/'\nrm: use --no-preserve-root to override this failsafe\n");
            return res;
        }
    }

    // 7. Sensitive system file access (cat /etc/shadow, etc.)
    for (int i = 1; i < token_count; i++)
    {
        if (strcmp(tokens[i], "/etc/shadow") == 0 ||
            strcmp(tokens[i], "/etc/gshadow") == 0 ||
            strcmp(tokens[i], "/etc/sudoers") == 0 ||
            strncmp(tokens[i], "/root", 5) == 0)
        {
            res.is_suspicious = 1;
            res.category = "Sensitive system file access";
            snprintf(res.simulated_output, sizeof(res.simulated_output),
                     "%s: %s: Permission denied\n", cmd, tokens[i]);
            return res;
        }
    }

    // 8. Package manager / system service manipulation
    if (strcmp(cmd, "apt") == 0 || strcmp(cmd, "apt-get") == 0 ||
        strcmp(cmd, "yum") == 0 || strcmp(cmd, "systemctl") == 0)
    {
        res.is_suspicious = 1;
        res.category = "Privileged system tool execution";
        snprintf(res.simulated_output, sizeof(res.simulated_output),
                 "E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\nE: Unable to acquire the dpkg frontend lock, are you root?\n");
        return res;
    }

    return res;
}
