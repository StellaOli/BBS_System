#ifndef MESSAGE_PROTOCOL_H
#define MESSAGE_PROTOCOL_H

#include <msgpack.h>
#include <string.h>
#include <stdint.h>
#include <time.h>  // ✅ ADICIONADO: Para time_t, struct tm

// ✅ CORREÇÃO: Todas as funções atualizadas com parâmetro clock
void create_login_message(const char* username, int64_t clock, msgpack_sbuffer* buffer);
void create_users_list_message(int64_t clock, msgpack_sbuffer* buffer);
void create_channel_message(const char* channel_name, int64_t clock, msgpack_sbuffer* buffer);
void create_publish_message(const char* user, const char* channel, const char* message, int64_t clock, msgpack_sbuffer* buffer);
void create_private_message(const char* src, const char* dst, const char* message, int64_t clock, msgpack_sbuffer* buffer);

int parse_message(const char* data, size_t size, msgpack_object* result);
int parse_pubsub_message(const char* data, size_t size, msgpack_object* result);
void extract_string_field(msgpack_object* data, const char* field, char* buffer, size_t buffer_size);
void extract_service_data(msgpack_object* data, char* status, size_t status_size, char* description, size_t desc_size);
void print_users_list(msgpack_object* data);
int64_t extract_clock_field(msgpack_object* data);



#endif