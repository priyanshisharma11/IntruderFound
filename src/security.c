#include <string.h>
#include "security.h"

const char *detect_suspicious(const char *command)
{
    if (strstr(command, "sudo") != NULL)
    {
        return "Privilege escalation attempt";
    }

    if (strstr(command, "rm -rf") != NULL)
    {
        return "Destructive file operation";
    }

    if (strstr(command, "chmod") != NULL)
    {
        return "File permission modification";
    }


    if (strstr(command, "passwd") != NULL)
    {
        return "Password modification attempt";
    }

    if (strstr(command, "/etc/shadow") != NULL)
    {
        return "Sensitive system file access";
    }

    if (strstr(command, "chown") != NULL)
    {
        return "File ownership modification";
    }

    return NULL;
}
