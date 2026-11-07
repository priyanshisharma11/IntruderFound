#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "editor.h"
#include "logger.h"
#include "security.h"

struct Node
{
    char name[64];
    char content[512];

    int is_directory;

    struct Node *parent;
    struct Node *children;
    struct Node *next;
};

typedef struct Node Node;

Node *create_node(char name[], int is_directory)
{
    Node *new_node = malloc(sizeof(Node));

    if (new_node == NULL)
    {
        printf("Memory allocation failed.\n");
        exit(1);
    }

    strcpy(new_node->name, name);
    new_node->content[0] = '\0';
    new_node->is_directory = is_directory;

    new_node->parent = NULL;
    new_node->children = NULL;
    new_node->next = NULL;

    return new_node;
}


Node *find_child(Node *directory, char name[])
{
    Node *temp = directory->children;

    while (temp != NULL)
    {
        if (strcmp(temp->name, name) == 0)
        {
            return temp;
        }

        temp = temp->next;
    }

    return NULL;
}


void add_child(Node *parent, Node *child)
{
    child->parent = parent;

    if (parent->children == NULL)
    {
        parent->children = child;
    }
    else
    {
        Node *temp = parent->children;

        while (temp->next != NULL)
        {
            temp = temp->next;
        }

        temp->next = child;
    }
}


void print_path(Node *directory)
{
    if (directory->parent != NULL)
    {
        print_path(directory->parent);
    }

    printf("/%s", directory->name);
}


void list_directory(Node *directory)
{
    Node *temp = directory->children;

    if (temp == NULL)
    {
        printf("Directory is empty.\n");
        return;
    }

    while (temp != NULL)
    {
        printf("%s", temp->name);

        if (temp->is_directory)
        {
            printf("/");
        }

        printf("  ");

        temp = temp->next;
    }

    printf("\n");
}


int valid_name(char name[])
{
    if (name[0] == '\0' ||
        strcmp(name, ".") == 0 ||
        strcmp(name, "..") == 0 ||
        strchr(name, '/') != NULL)
    {
        return 0;
    }

    return 1;
}

// Remove unnecessary spaces from the beginning and end
void trim_spaces(char text[])
{
    int start = 0;
    int end = strlen(text) - 1;

    while (text[start] == ' ' || text[start] == '\t')
    {
        start++;
    }

    while (end >= start &&
           (text[end] == ' ' || text[end] == '\t'))
    {
        text[end] = '\0';
        end--;
    }

    if (start > 0)
    {
        memmove(text, text + start, strlen(text + start) + 1);
    }
}


// Process echo and simulated redirection
void process_echo(Node *current_dir, char input[])
{
    char text[256];
    char filename[64];
    char *redirect;
    char *content_start;

    int append = 0;

    // Skip the word "echo "
    content_start = input + 4;

    while (*content_start == ' ')
    {
        content_start++;
    }

    // Check for append operator >>
    redirect = strstr(content_start, ">>");

    if (redirect != NULL)
    {
        append = 1;
    }
    else
    {
        // Check for overwrite operator >
        redirect = strchr(content_start, '>');
    }

    if (redirect == NULL)
    {
        snprintf(text, sizeof(text), "%s", content_start);
        trim_spaces(text);

        int len = strlen(text);

        if (len >= 2 && text[0] == '"' && text[len - 1] == '"')
        {
            memmove(text, text + 1, len - 2);
            text[len - 2] = '\0';
        }

        printf("%s\n", text);
        return;
    }

    // Extract text before the redirection operator
    int text_length = redirect - content_start;

    if (text_length >= (int)sizeof(text))
    {
        printf("echo: text is too long\n");
        return;
    }

    strncpy(text, content_start, text_length);
    text[text_length] = '\0';

    trim_spaces(text);

    // Remove surrounding double quotes
    int len = strlen(text);

    if (len >= 2 && text[0] == '"' && text[len - 1] == '"')
    {
        memmove(text, text + 1, len - 2);
        text[len - 2] = '\0';
    }

    // Get destination filename
    char *filename_start = redirect + (append ? 2 : 1);

    while (*filename_start == ' ')
    {
        filename_start++;
    }

    if (sscanf(filename_start, "%63s", filename) != 1 ||
        !valid_name(filename))
    {
        printf("echo: invalid filename\n");
        return;
    }

    // Find existing file or create a new one
    Node *file = find_child(current_dir, filename);

    if (file != NULL && file->is_directory)
    {
        printf("echo: cannot write to a directory\n");
        return;
    }

    if (file == NULL)
    {
        file = create_node(filename, 0);
        add_child(current_dir, file);
    }

    // Write or append content
    int current_length = strlen(file->content);
    int text_length_new = strlen(text);

    if (current_length + text_length_new + 2 >
        (int)sizeof(file->content))
    {
        printf("echo: file content limit exceeded\n");
        return;
    }

    if (append)
    {
        if (current_length > 0)
        {
            file->content[current_length] = '\n';
            current_length++;
        }

        strcpy(file->content + current_length, text);
    }
    else
    {
        strcpy(file->content, text);
    }

    // Echo normally adds a newline
    strcat(file->content, "\n");

    printf("Content written successfully.\n");
}

int main()
{
    char input[256];
    char command[32];
    char argument[64];

    // Create home directory
    Node *root = create_node("home", 1);
    Node *user = create_node("intruder", 1);

    add_child(root, user);

    Node *current_dir = user;

    // Create initial virtual directories
    Node *documents = create_node("Documents", 1);
    Node *downloads = create_node("Downloads", 1);

    add_child(user, documents);
    add_child(user, downloads);

    // Create initial virtual files
    Node *secrets = create_node("secrets.txt", 0);
    strcpy(secrets->content, "This is a confidential file.");

    add_child(user, secrets);

    Node *notes = create_node("notes.txt", 0);
    strcpy(notes->content, "These are personal notes.");

    add_child(documents, notes);

    Node *assignment = create_node("assignment.txt", 0);
    strcpy(assignment->content, "UNIX Programming Assignment");

    add_child(documents, assignment);

    Node *report = create_node("report.pdf", 0);
    strcpy(report->content, "Simulated PDF report.");

    add_child(downloads, report);

    Node *image = create_node("image.jpg", 0);
    strcpy(image->content, "Simulated image file.");

    add_child(downloads, image);

    logger_start();

    printf("====================================\n");
    printf("       INTRUDFOUND DECOY SHELL\n");
    printf("====================================\n");

    printf("Welcome, intruder!\n");
    printf("Type help to see available commands.\n\n");


    while (1)
    {
        printf("intruder@decoy:");

        if (current_dir == user)
        {
            printf("~");
        }
        else
        {
            print_path(current_dir);
        }

        printf("$ ");
        fflush(stdout);


        if (fgets(input, sizeof(input), stdin) == NULL)
        {
	    logger_end();
            printf("\nSession ended.\n");
            break;
        }

        input[strcspn(input, "\n")] = '\0';

        command[0] = '\0';
        argument[0] = '\0';

        sscanf(input, "%31s %63s", command, argument);


        if (input[0] == '\0')
        {
            continue;
        }

	logger_log("COMMAND", input);

	// Check for suspicious commands
	const char *reason = detect_suspicious(input);

	if (reason != NULL)
	{
		logger_log("SUSPICIOUS", reason);

    		printf("\n[SECURITY ALERT] Suspicious command detected!\n");
    		printf("Category: %s\n", reason);
   		printf("Command blocked by IntruderFound.\n\n");

   		continue;
	}

        if (strcmp(command, "exit") == 0)
        {
	    logger_end();
            printf("Session ended.\n");
            break;
        }

        else if (strcmp(command, "help") == 0)
        {
            printf("Available commands:\n");
            printf("help, pwd, ls, whoami, cd, mkdir, touch, cat, exit\n");
        }

        else if (strcmp(command, "whoami") == 0)
        {
            printf("intruder\n");
        }

        else if (strcmp(command, "pwd") == 0)
        {
            print_path(current_dir);
            printf("\n");
        }

        else if (strcmp(command, "ls") == 0)
        {
            list_directory(current_dir);
        }

        else if (strcmp(command, "cd") == 0)
        {
            if (argument[0] == '\0' || strcmp(argument, "~") == 0)
            {
                current_dir = user;
            }

            else if (strcmp(argument, "..") == 0)
            {
                if (current_dir->parent != NULL &&
                    current_dir->parent != root)
                {
                    current_dir = current_dir->parent;
                }
            }

            else
            {
                Node *target = find_child(current_dir, argument);

                if (target != NULL && target->is_directory)
                {
                    current_dir = target;
                }
                else
                {
                    printf("cd: directory not found\n");
                }
            }
        }

        else if (strcmp(command, "mkdir") == 0)
        {
            if (!valid_name(argument))
            {
                printf("mkdir: invalid directory name\n");
            }
            else if (find_child(current_dir, argument) != NULL)
            {
                printf("mkdir: directory or file already exists\n");
            }
            else
            {
                Node *new_dir = create_node(argument, 1);
                add_child(current_dir, new_dir);

                printf("Directory created successfully.\n");
            }
        }

        else if (strcmp(command, "touch") == 0)
        {
            if (!valid_name(argument))
            {
                printf("touch: invalid file name\n");
            }
            else if (find_child(current_dir, argument) != NULL)
            {
                printf("touch: file already exists\n");
            }
            else
            {
                Node *new_file = create_node(argument, 0);
                add_child(current_dir, new_file);

                printf("File created successfully.\n");
            }
        }

        else if (strcmp(command, "cat") == 0)
        {
            Node *file = find_child(current_dir, argument);

            if (file == NULL || file->is_directory)
            {
                printf("cat: file not found\n");
            }
            else
            {
                printf("%s\n", file->content);
            }
        }

	else if (strcmp(command, "echo") == 0)
	{
	    process_echo(current_dir, input);
	}
	else if (strcmp(command, "vi") == 0)
	{
		if (!valid_name(argument))
    		{
        		printf("vi: invalid filename\n");
    		}
    		else
    		{
        		Node *file = find_child(current_dir, argument);

        		if (file != NULL && file->is_directory)
        		{
            			printf("vi: cannot edit a directory\n");
        		}
        		else
        		{
            			if (file == NULL)
           			{
					file = create_node(argument, 0);
                			add_child(current_dir, file);
           			}

           			open_editor(file->content, sizeof(file->content), file->name);
        		}
    		}
	}
        else
        {
            printf("%s: command not found\n", command);
        }
    }

    return 0;
}
