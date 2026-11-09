.RECIPEPREFIX := >

CC = gcc
CFLAGS = -Wall -Wextra -std=c11

SRC = src/main.c src/editor.c src/logger.c src/security.c src/signals.c

TARGET = intruderfound

all: $(TARGET)

$(TARGET): $(SRC)
>$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

run: $(TARGET)
>./$(TARGET)

inspect:
>./scripts/inspect.sh

clean:
>rm -f $(TARGET)

.PHONY: all run inspect clean

