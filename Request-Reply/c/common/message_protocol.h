#ifndef MESSAGE_PROTOCOL_H
#define MESSAGE_PROTOCOL_H

#include <msgpack.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// Estruturas para mensagens
typedef struct {
    char service[32];
    msgpack_object data;
} bbs_message_t;

// Funções do protocolo
void get_current_timestamp(char* buffer, size_t size);
void create_login_message(const char* username, msgpack_sbuffer* sbuf);
void create_users_list_message(msgpack_sbuffer* sbuf);
void create_channel_message(const char* channel_name, msgpack_sbuffer* sbuf);
void create_publish_message(const char* user, const char* channel, const char* message, msgpack_sbuffer* sbuf);
void create_private_message(const char* src, const char* dst, const char* message, msgpack_sbuffer* sbuf);
int parse_message(const char* data, size_t size, msgpack_object* result);
int parse_pubsub_message(const char* data, size_t size, msgpack_object* result);
void extract_string_field(msgpack_object* obj, const char* field, char* buffer, size_t buffer_size);
void extract_service_data(msgpack_object* root, char* status, size_t status_size, char* description, size_t desc_size);
void print_users_list(msgpack_object* root);

#endif