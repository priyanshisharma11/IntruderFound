#include <stdio.h>
#include <string.h>

int main()
{
    char input[256];
    char command[32];
    char argument[128];

    char current_dir[128] = "/home/intruder";

    printf("====================================\n");
    printf("       INTRUDFOUND DECOY SHELL\n");
    printf("====================================\n");

    printf("Welcome, intruder!\n");
    printf("Type help to see available commands.\n\n");

    while (1)
    {
        printf("intruder@decoy:%s$ ", current_dir);
        fflush(stdout);

        if (fgets(input, sizeof(input), stdin) == NULL)
        {
            printf("\nSession ended.\n");
            break;
        }

        input[strcspn(input, "\n")] = '\0';

        command[0] = '\0';
        argument[0] = '\0';

        sscanf(input, "%31s %127s", command, argument);

        if (strcmp(command, "exit") == 0)
        {
            printf("Session ended.\n");
            break;
        }

        else if (strcmp(command, "help") == 0)
        {
            printf("Available commands:\n");
            printf("help, pwd, ls, whoami, cd, exit\n");
        }

        else if (strcmp(command, "pwd") == 0)
        {
            printf("%s\n", current_dir);
        }

        else if (strcmp(command, "whoami") == 0)
        {
            printf("intruder\n");
        }

        else if (strcmp(command, "ls") == 0)
        {
            if (strcmp(current_dir, "/home/intruder") == 0)
            {
                printf("Documents  Downloads  secrets.txt\n");
            }
            else if (strcmp(current_dir, "/home/intruder/Documents") == 0)
            {
                printf("notes.txt  assignment.txt\n");
            }
            else if (strcmp(current_dir, "/home/intruder/Downloads") == 0)
            {
                printf("report.pdf  image.jpg\n");
            }
        }

        else if (strcmp(command, "cd") == 0)
        {
            if (argument[0] == '\0')
            {
                strcpy(current_dir, "/home/intruder");
            }

            else if (strcmp(argument, "Documents") == 0 &&
                     strcmp(current_dir, "/home/intruder") == 0)
            {
                strcat(current_dir, "/Documents");
            }

            else if (strcmp(argument, "Downloads") == 0 &&
                     strcmp(current_dir, "/home/intruder") == 0)
            {
                strcat(current_dir, "/Downloads");
            }

            else if (strcmp(argument, "..") == 0)
            {
                if (strcmp(current_dir, "/home/intruder/Documents") == 0 ||
                    strcmp(current_dir, "/home/intruder/Downloads") == 0)
                {
                    strcpy(current_dir, "/home/intruder");
                }
                else
                {
                    printf("Already at home directory.\n");
                }
            }

            else
            {
                printf("cd: directory not found\n");
            }
        }

        else if (input[0] == '\0')
        {
            continue;
        }

        else
        {
            printf("%s: command not found\n", command);
        }
    }

    return 0;
}
