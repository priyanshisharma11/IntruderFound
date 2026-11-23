CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE

SRC = src/main.c src/editor.c src/logger.c src/security.c src/signals.c

TARGET = intruderfound

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

run: $(TARGET)
	./$(TARGET)

inspect:
	./scripts/inspect.sh

clean:
	rm -f $(TARGET)

.PHONY: all run inspect clean
