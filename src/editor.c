#include <stdio.h>
#include <string.h>
#include "editor.h"

void open_editor(char *content, size_t capacity, const char *filename)
{
    char buffer[512];
    char input[256];

    int mode = 0;  // 0 = NORMAL, 1 = INSERT

    // Copy existing file content into editor buffer
    snprintf(buffer, sizeof(buffer), "%s", content);

    printf("\n");
    printf("====================================\n");
    printf("          INTRUDFOUND VI\n");
    printf("====================================\n");

    printf("Editing file: %s\n", filename);
    printf("\nCurrent content:\n");

    if (buffer[0] == '\0')
    {
        printf("(Empty file)\n");
    }
    else
    {
        printf("%s", buffer);
    }

    printf("\nNORMAL MODE\n");
    printf("Type i to enter INSERT mode.\n");
    printf("Type :w to save, :q to quit, :wq to save and quit.\n");
    printf("Type :q! to quit without saving.\n\n");

    while (1)
    {
        if (mode == 0)
        {
            printf("-- NORMAL MODE --\n");
        }
        else
        {
            printf("-- INSERT MODE --\n");
        }

        printf("vi> ");
        fflush(stdout);

        if (fgets(input, sizeof(input), stdin) == NULL)
        {
            printf("\nEditor closed.\n");
            return;
        }

        input[strcspn(input, "\n")] = '\0';

        // NORMAL MODE
        if (mode == 0)
        {
            if (strcmp(input, "i") == 0)
            {
                mode = 1;
                printf("Entered INSERT mode.\n");
            }

            else if (strcmp(input, ":w") == 0)
            {
                snprintf(content, capacity, "%s", buffer);
                printf("File saved successfully.\n");
            }

            else if (strcmp(input, ":q") == 0)
            {
                printf("Editor closed.\n");
                break;
            }

            else if (strcmp(input, ":wq") == 0)
            {
                snprintf(content, capacity, "%s", buffer);
                printf("File saved successfully.\n");
                printf("Editor closed.\n");
                break;
            }

            else if (strcmp(input, ":q!") == 0)
            {
                printf("Changes discarded. Editor closed.\n");
                break;
            }

            else
            {
                printf("Unknown editor command.\n");
            }
        }

        // INSERT MODE
        else
        {
            if (strcmp(input, "ESC") == 0)
            {
                mode = 0;
                printf("Returned to NORMAL mode.\n");
            }

            else
            {
                size_t current_length = strlen(buffer);
                size_t new_length = strlen(input);

                if (current_length + new_length + 2 >= sizeof(buffer))
                {
                    printf("Editor buffer is full.\n");
                }
                else
                {
                    memcpy(buffer + current_length, input, new_length);
                    current_length += new_length;

                    buffer[current_length] = '\n';
                    buffer[current_length + 1] = '\0';
                }
            }
        }
    }
}

