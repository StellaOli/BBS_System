#include "message_protocol.h"
#include <time.h>
#include <stdio.h>
#include <string.h>

// ✅ CORREÇÃO: Adicionar includes faltantes
#include <time.h>

// Timestamp atual em ISO format
void get_current_timestamp(char* buffer, size_t size) {
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%SZ", tm_info);
}

// ✅ CORREÇÃO: Todas as funções atualizadas com parâmetro clock
void create_login_message(const char* username, int64_t clock, msgpack_sbuffer* sbuf) {
    msgpack_packer pk;
    char timestamp[32];
    
    get_current_timestamp(timestamp, sizeof(timestamp));
    msgpack_sbuffer_init(sbuf);
    msgpack_packer_init(&pk, sbuf, msgpack_sbuffer_write);
    
    msgpack_pack_map(&pk, 3); // ✅ MUDADO: 3 elementos (service, data, clock)
    
    // service
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "service", 7);
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "login", 5);
    
    // data
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "data", 4);
    msgpack_pack_map(&pk, 2);
    
    // user
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "user", 4);
    msgpack_pack_str(&pk, strlen(username));
    msgpack_pack_str_body(&pk, username, strlen(username));
    
    // timestamp
    msgpack_pack_str(&pk, 9);
    msgpack_pack_str_body(&pk, "timestamp", 9);
    msgpack_pack_str(&pk, strlen(timestamp));
    msgpack_pack_str_body(&pk, timestamp, strlen(timestamp));
    
    // ✅ NOVO: clock
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "clock", 5);
    msgpack_pack_int64(&pk, clock);
}

void create_users_list_message(int64_t clock, msgpack_sbuffer* sbuf) {
    msgpack_packer pk;
    char timestamp[32];
    
    get_current_timestamp(timestamp, sizeof(timestamp));
    msgpack_sbuffer_init(sbuf);
    msgpack_packer_init(&pk, sbuf, msgpack_sbuffer_write);
    
    msgpack_pack_map(&pk, 3); // ✅ MUDADO: 3 elementos
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "service", 7);
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "users", 5);
    
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "data", 4);
    msgpack_pack_map(&pk, 1);
    
    msgpack_pack_str(&pk, 9);
    msgpack_pack_str_body(&pk, "timestamp", 9);
    msgpack_pack_str(&pk, strlen(timestamp));
    msgpack_pack_str_body(&pk, timestamp, strlen(timestamp));
    
    // ✅ NOVO: clock
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "clock", 5);
    msgpack_pack_int64(&pk, clock);
}

void create_channel_message(const char* channel_name, int64_t clock, msgpack_sbuffer* sbuf) {
    msgpack_packer pk;
    char timestamp[32];
    
    get_current_timestamp(timestamp, sizeof(timestamp));
    msgpack_sbuffer_init(sbuf);
    msgpack_packer_init(&pk, sbuf, msgpack_sbuffer_write);
    
    msgpack_pack_map(&pk, 3); // ✅ MUDADO: 3 elementos
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "service", 7);
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "channel", 7);
    
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "data", 4);
    msgpack_pack_map(&pk, 2);
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "channel", 7);
    msgpack_pack_str(&pk, strlen(channel_name));
    msgpack_pack_str_body(&pk, channel_name, strlen(channel_name));
    
    msgpack_pack_str(&pk, 9);
    msgpack_pack_str_body(&pk, "timestamp", 9);
    msgpack_pack_str(&pk, strlen(timestamp));
    msgpack_pack_str_body(&pk, timestamp, strlen(timestamp));
    
    // ✅ NOVO: clock
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "clock", 5);
    msgpack_pack_int64(&pk, clock);
}

void create_publish_message(const char* user, const char* channel, const char* message, int64_t clock, msgpack_sbuffer* sbuf) {
    msgpack_packer pk;
    char timestamp[32];
    
    get_current_timestamp(timestamp, sizeof(timestamp));
    msgpack_sbuffer_init(sbuf);
    msgpack_packer_init(&pk, sbuf, msgpack_sbuffer_write);
    
    msgpack_pack_map(&pk, 3); // ✅ MUDADO: 3 elementos
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "service", 7);
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "publish", 7);
    
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "data", 4);
    msgpack_pack_map(&pk, 4);
    
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "user", 4);
    msgpack_pack_str(&pk, strlen(user));
    msgpack_pack_str_body(&pk, user, strlen(user));
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "channel", 7);
    msgpack_pack_str(&pk, strlen(channel));
    msgpack_pack_str_body(&pk, channel, strlen(channel));
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "message", 7);
    msgpack_pack_str(&pk, strlen(message));
    msgpack_pack_str_body(&pk, message, strlen(message));
    
    msgpack_pack_str(&pk, 9);
    msgpack_pack_str_body(&pk, "timestamp", 9);
    msgpack_pack_str(&pk, strlen(timestamp));
    msgpack_pack_str_body(&pk, timestamp, strlen(timestamp));
    
    // ✅ NOVO: clock
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "clock", 5);
    msgpack_pack_int64(&pk, clock);
}

void create_private_message(const char* src, const char* dst, const char* message, int64_t clock, msgpack_sbuffer* sbuf) {
    msgpack_packer pk;
    char timestamp[32];
    
    get_current_timestamp(timestamp, sizeof(timestamp));
    msgpack_sbuffer_init(sbuf);
    msgpack_packer_init(&pk, sbuf, msgpack_sbuffer_write);
    
    msgpack_pack_map(&pk, 3); // ✅ MUDADO: 3 elementos
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "service", 7);
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "message", 7);
    
    msgpack_pack_str(&pk, 4);
    msgpack_pack_str_body(&pk, "data", 4);
    msgpack_pack_map(&pk, 4);
    
    msgpack_pack_str(&pk, 3);
    msgpack_pack_str_body(&pk, "src", 3);
    msgpack_pack_str(&pk, strlen(src));
    msgpack_pack_str_body(&pk, src, strlen(src));
    
    msgpack_pack_str(&pk, 3);
    msgpack_pack_str_body(&pk, "dst", 3);
    msgpack_pack_str(&pk, strlen(dst));
    msgpack_pack_str_body(&pk, dst, strlen(dst));
    
    msgpack_pack_str(&pk, 7);
    msgpack_pack_str_body(&pk, "message", 7);
    msgpack_pack_str(&pk, strlen(message));
    msgpack_pack_str_body(&pk, message, strlen(message));
    
    msgpack_pack_str(&pk, 9);
    msgpack_pack_str_body(&pk, "timestamp", 9);
    msgpack_pack_str(&pk, strlen(timestamp));
    msgpack_pack_str_body(&pk, timestamp, strlen(timestamp));
    
    // ✅ NOVO: clock
    msgpack_pack_str(&pk, 5);
    msgpack_pack_str_body(&pk, "clock", 5);
    msgpack_pack_int64(&pk, clock);
}

// Parsear mensagem
int parse_message(const unsigned char* data, size_t size, msgpack_object* result) {
    msgpack_unpacked unpacked;
    msgpack_unpacked_init(&unpacked);
    
    if (msgpack_unpack_next(&unpacked, data, size, NULL)) {
        *result = unpacked.data;
        msgpack_unpacked_destroy(&unpacked);
        return 0;
    }
    
    msgpack_unpacked_destroy(&unpacked);
    return -1;
}

// Parsear mensagem Pub/Sub
int parse_pubsub_message(const unsigned char* data, size_t size, msgpack_object* result) {
    return parse_message((const unsigned char*)data, size, result);
}

// Extrair campo string de um objeto
void extract_string_field(msgpack_object* obj, const char* field, char* buffer, size_t buffer_size) {
    if (obj->type == MSGPACK_OBJECT_MAP) {
        for (int i = 0; i < obj->via.map.size; i++) {
            msgpack_object key = obj->via.map.ptr[i].key;
            msgpack_object val = obj->via.map.ptr[i].val;
            
            if (key.type == MSGPACK_OBJECT_STR && 
                strncmp(key.via.str.ptr, field, key.via.str.size) == 0 &&
                val.type == MSGPACK_OBJECT_STR) {
                
                size_t copy_size = val.via.str.size < buffer_size - 1 ? 
                                 val.via.str.size : buffer_size - 1;
                strncpy(buffer, val.via.str.ptr, copy_size);
                buffer[copy_size] = '\0';
                return;
            }
        }
    }
    buffer[0] = '\0';
}

// Extrair dados de serviço (status e description)
void extract_service_data(msgpack_object* root, char* status, size_t status_size, 
                         char* description, size_t desc_size) {
    if (root->type == MSGPACK_OBJECT_MAP) {
        for (int i = 0; i < root->via.map.size; i++) {
            msgpack_object key = root->via.map.ptr[i].key;
            
            if (key.type == MSGPACK_OBJECT_STR && 
                strncmp(key.via.str.ptr, "data", key.via.str.size) == 0) {
                
                msgpack_object data = root->via.map.ptr[i].val;
                if (data.type == MSGPACK_OBJECT_MAP) {
                    extract_string_field(&data, "status", status, status_size);
                    extract_string_field(&data, "description", description, desc_size);
                }
                return;
            }
        }
    }
}

// Imprimir lista de usuários
void print_users_list(msgpack_object* root) {
    if (root->type == MSGPACK_OBJECT_MAP) {
        for (int i = 0; i < root->via.map.size; i++) {
            msgpack_object key = root->via.map.ptr[i].key;
            
            if (key.type == MSGPACK_OBJECT_STR && 
                strncmp(key.via.str.ptr, "data", key.via.str.size) == 0) {
                
                msgpack_object data = root->via.map.ptr[i].val;
                if (data.type == MSGPACK_OBJECT_MAP) {
                    for (int j = 0; j < data.via.map.size; j++) {
                        msgpack_object key2 = data.via.map.ptr[j].key;
                        msgpack_object val2 = data.via.map.ptr[j].val;
                        
                        if (key2.type == MSGPACK_OBJECT_STR && 
                            strncmp(key2.via.str.ptr, "users", key2.via.str.size) == 0 &&
                            val2.type == MSGPACK_OBJECT_ARRAY) {
                            
                            printf("\n👥 Usuários cadastrados:\n");
                            for (int k = 0; k < val2.via.array.size; k++) {
                                msgpack_object user = val2.via.array.ptr[k];
                                if (user.type == MSGPACK_OBJECT_STR) {
                                    printf("  - %.*s\n", user.via.str.size, user.via.str.ptr);
                                }
                            }
                            return;
                        }
                    }
                }
            }
        }
    }
    printf("  📭 Nenhum usuário cadastrado\n");
}

// ✅ NOVO: Extrair campo clock
int64_t extract_clock_field(msgpack_object* data) {
    msgpack_object_map* map = &data->via.map;
    for (uint32_t i = 0; i < map->size; i++) {
        msgpack_object_kv* kv = &map->ptr[i];
        if (kv->key.type == MSGPACK_OBJECT_STR) {
            char key[32];
            snprintf(key, sizeof(key), "%.*s", 
                    kv->key.via.str.size, kv->key.via.str.ptr);
            if (strcmp(key, "clock") == 0 && kv->val.type == MSGPACK_OBJECT_POSITIVE_INTEGER) {
                return kv->val.via.u64;
            }
        }
    }
    return 0;
}