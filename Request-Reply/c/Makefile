CC = gcc
CFLAGS = -Wall -g -std=c99 -pthread
LIBS = -lzmq -lmsgpackc -lreadline
TARGET_CLIENT = client
TARGET_AUTO = auto_client
SOURCES_CLIENT = client.c common/message_protocol.c common/logical_clock.c
SOURCES_AUTO = auto_client.c common/message_protocol.c common/logical_clock.c

all: $(TARGET_CLIENT) $(TARGET_AUTO)

$(TARGET_CLIENT): $(SOURCES_CLIENT)
	$(CC) $(CFLAGS) -I. -o $(TARGET_CLIENT) $(SOURCES_CLIENT) $(LIBS)

$(TARGET_AUTO): $(SOURCES_AUTO)
	$(CC) $(CFLAGS) -I. -o $(TARGET_AUTO) $(SOURCES_AUTO) $(LIBS)

clean:
	rm -f $(TARGET_CLIENT) $(TARGET_AUTO)

install-deps:
	# Ubuntu/Debian
	# sudo apt-get install libzmq3-dev libmsgpack-dev libreadline-dev

.PHONY: all clean install-deps

clean:
	rm -f $(TARGET_CLIENT) $(TARGET_AUTO)

install-deps:
	# Ubuntu/Debian
	# sudo apt-get install libzmq3-dev libmsgpack-dev libreadline-dev

.PHONY: all clean install-deps