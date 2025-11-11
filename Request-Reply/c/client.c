#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <msgpack.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <pthread.h>

#define BROKER_ENDPOINT "tcp://broker:5555"
#define PUBSUB_ENDPOINT "tcp://pubsub-proxy:5558"

typedef struct {
    void* context;
    void* req_socket;
    void* sub_socket;
    char current_user[32];
    int receiving;
} bbs_client_t;

#include "common/message_protocol.h"

void print_help() {
    printf("\n📋 Comandos disponíveis:\n");
    printf("  login <nome>          - Fazer login com nome de usuário\n");
    printf("  users                 - Listar todos os usuários\n");
    printf("  channel <nome>        - Criar um novo canal\n");
    printf("  channels              - Listar todos os canais\n");
    printf("  pub <canal> <msg>     - Publicar mensagem em canal\n");
    printf("  msg <user> <msg>      - Enviar mensagem privada\n");
    printf("  sub <canal>           - Inscrever em canal\n");
    printf("  unsub <canal>         - Cancelar inscrição\n");
    printf("  history               - Histórico de mensagens\n");
    printf("  help                  - Mostrar esta ajuda\n");
    printf("  quit                  - Sair do programa\n");
}

int send_request(bbs_client_t* client, msgpack_sbuffer* request, msgpack_sbuffer* response) {
    // Enviar requisição
    if (zmq_send(client->req_socket, request->data, request->size, 0) == -1) {
        printf("❌ Erro ao enviar mensagem\n");
        return -1;
    }

    // ✅ CORREÇÃO: Usar buffer direto ou zmq_msg_recv
    char reply_buffer[4096];
    int recv_result = zmq_recv(client->req_socket, reply_buffer, sizeof(reply_buffer) - 1, 0);
    if (recv_result == -1) {
        printf("❌ Erro ao receber resposta\n");
        return -1;
    }

    // Copiar dados para buffer de resposta
    msgpack_sbuffer_clear(response);
    msgpack_sbuffer_write(response, reply_buffer, recv_result);
    
    printf("📥 Resposta recebida: %d bytes\n", recv_result);
    return 0;
}

void subscribe_to_topic(bbs_client_t* client, const char* topic) {
    zmq_setsockopt(client->sub_socket, ZMQ_SUBSCRIBE, topic, strlen(topic));
    printf("✅ Inscrito no tópico: %s\n", topic);
}

void unsubscribe_from_topic(bbs_client_t* client, const char* topic) {
    zmq_setsockopt(client->sub_socket, ZMQ_UNSUBSCRIBE, topic, strlen(topic));
    printf("✅ Inscrição cancelada do tópico: %s\n", topic);
}

void* receive_messages(void* arg) {
    bbs_client_t* client = (bbs_client_t*)arg;
    
    while (client->receiving) {
        // ✅ CORREÇÃO: Usar buffer direto
        char msg_buffer[4096];
        
        // Timeout de 1 segundo
        int timeout_ms = 1000;
        zmq_setsockopt(client->sub_socket, ZMQ_RCVTIMEO, &timeout_ms, sizeof(timeout_ms));
        
        int recv_result = zmq_recv(client->sub_socket, msg_buffer, sizeof(msg_buffer) - 1, 0);
        if (recv_result != -1) {
            // Parsear mensagem Pub/Sub
            msgpack_object data;
            if (parse_pubsub_message(msg_buffer, recv_result, &data) == 0) {
                // Extrair dados da mensagem
                char sender[32] = "Desconhecido";
                char content[256] = "";
                char target[32] = "";
                
                extract_string_field(&data, "sender", sender, sizeof(sender));
                extract_string_field(&data, "content", content, sizeof(content));
                extract_string_field(&data, "target", target, sizeof(target));
                
                if (strncmp(target, "channel.", 8) == 0) {
                    printf("\n📢 [#%s] %s: %s\n", target + 8, sender, content);
                } else {
                    printf("\n📩 [PRIVADO] %s: %s\n", sender, content);
                }
            }
        }
    }
    
    return NULL;
}

int login_user(bbs_client_t* client, const char* username) {
    msgpack_sbuffer request, response;
    msgpack_sbuffer_init(&request);
    msgpack_sbuffer_init(&response);
    
    // Criar mensagem de login
    create_login_message(username, &request);
    
    // Enviar e receber resposta
    if (send_request(client, &request, &response) != 0) {
        msgpack_sbuffer_destroy(&request);
        msgpack_sbuffer_destroy(&response);
        return -1;
    }
    
    // Parsear resposta
    msgpack_object data;
    if (parse_message(response.data, response.size, &data) == 0) {
        char status[16] = "";
        char description[128] = "";
        
        extract_service_data(&data, status, sizeof(status), description, sizeof(description));
        
        if (strcmp(status, "sucesso") == 0) {
            strncpy(client->current_user, username, sizeof(client->current_user) - 1);
            printf("✅ %s\n", description);
            
            // Inscrever no tópico do usuário
            char user_topic[64];
            snprintf(user_topic, sizeof(user_topic), "user.%s", username);
            subscribe_to_topic(client, user_topic);
            
            // Iniciar thread de recebimento
            client->receiving = 1;
            pthread_t receive_thread;
            pthread_create(&receive_thread, NULL, receive_messages, client);
            pthread_detach(receive_thread);
            
            msgpack_sbuffer_destroy(&request);
            msgpack_sbuffer_destroy(&response);
            return 0;
        } else {
            printf("❌ %s\n", description);
        }
    }
    
    msgpack_sbuffer_destroy(&request);
    msgpack_sbuffer_destroy(&response);
    return -1;
}

int list_users(bbs_client_t* client) {
    msgpack_sbuffer request, response;
    msgpack_sbuffer_init(&request);
    msgpack_sbuffer_init(&response);
    
    create_users_list_message(&request);
    
    if (send_request(client, &request, &response) != 0) {
        msgpack_sbuffer_destroy(&request);
        msgpack_sbuffer_destroy(&response);
        return -1;
    }
    
    msgpack_object data;
    if (parse_message(response.data, response.size, &data) == 0) {
        printf("\n👥 Usuários cadastrados:\n");
        print_users_list(&data);
    }
    
    msgpack_sbuffer_destroy(&request);
    msgpack_sbuffer_destroy(&response);
    return 0;
}

int create_channel(bbs_client_t* client, const char* channel_name) {
    if (strlen(client->current_user) == 0) {
        printf("❌ Você precisa estar logado\n");
        return -1;
    }
    
    msgpack_sbuffer request, response;
    msgpack_sbuffer_init(&request);
    msgpack_sbuffer_init(&response);
    
    create_channel_message(channel_name, &request);
    
    if (send_request(client, &request, &response) != 0) {
        msgpack_sbuffer_destroy(&request);
        msgpack_sbuffer_destroy(&response);
        return -1;
    }
    
    msgpack_object data;
    if (parse_message(response.data, response.size, &data) == 0) {
        char status[16] = "";
        char description[128] = "";
        
        extract_service_data(&data, status, sizeof(status), description, sizeof(description));
        
        if (strcmp(status, "sucesso") == 0) {
            printf("✅ %s\n", description);
        } else {
            printf("❌ %s\n", description);
        }
    }
    
    msgpack_sbuffer_destroy(&request);
    msgpack_sbuffer_destroy(&response);
    return 0;
}

int publish_message(bbs_client_t* client, const char* channel, const char* message) {
    if (strlen(client->current_user) == 0) {
        printf("❌ Você precisa estar logado\n");
        return -1;
    }
    
    msgpack_sbuffer request, response;
    msgpack_sbuffer_init(&request);
    msgpack_sbuffer_init(&response);
    
    create_publish_message(client->current_user, channel, message, &request);
    
    if (send_request(client, &request, &response) != 0) {
        msgpack_sbuffer_destroy(&request);
        msgpack_sbuffer_destroy(&response);
        return -1;
    }
    
    msgpack_object data;
    if (parse_message(response.data, response.size, &data) == 0) {
        char status[16] = "";
        char description[128] = "";
        
        extract_service_data(&data, status, sizeof(status), description, sizeof(description));
        
        if (strcmp(status, "OK") == 0) {
            printf("✅ %s\n", description);
        } else {
            printf("❌ %s\n", description);
        }
    }
    
    msgpack_sbuffer_destroy(&request);
    msgpack_sbuffer_destroy(&response);
    return 0;
}

int send_private_message(bbs_client_t* client, const char* destination, const char* message) {
    if (strlen(client->current_user) == 0) {
        printf("❌ Você precisa estar logado\n");
        return -1;
    }
    
    msgpack_sbuffer request, response;
    msgpack_sbuffer_init(&request);
    msgpack_sbuffer_init(&response);
    
    create_private_message(client->current_user, destination, message, &request);
    
    if (send_request(client, &request, &response) != 0) {
        msgpack_sbuffer_destroy(&request);
        msgpack_sbuffer_destroy(&response);
        return -1;
    }
    
    msgpack_object data;
    if (parse_message(response.data, response.size, &data) == 0) {
        char status[16] = "";
        char description[128] = "";
        
        extract_service_data(&data, status, sizeof(status), description, sizeof(description));
        
        if (strcmp(status, "OK") == 0) {
            printf("✅ %s\n", description);
        } else {
            printf("❌ %s\n", description);
        }
    }
    
    msgpack_sbuffer_destroy(&request);
    msgpack_sbuffer_destroy(&response);
    return 0;
}

void start_interactive(bbs_client_t* client) {
    printf("=== 🚀 Sistema BBS - Cliente ===\n");
    printf("Digite 'help' para ver os comandos disponíveis\n");
    
    char* line;
    char prompt[64];
    
    while (1) {
        // ✅ CORREÇÃO: Criar prompt separadamente
        if (client->current_user[0]) {
            snprintf(prompt, sizeof(prompt), "[%s]> ", client->current_user);
        } else {
            snprintf(prompt, sizeof(prompt), "[desconectado]> ");
        }
        
        line = readline(prompt);
        if (line == NULL) {
            break; // EOF (Ctrl+D)
        }
        
        if (strlen(line) == 0) {
            free(line);
            continue;
        }
        
        add_history(line);
        
        // Processar comando
        char command[32], arg1[64], arg2[256];
        int args = sscanf(line, "%31s %63s %255[^\n]", command, arg1, arg2);
        
        if (strcmp(command, "quit") == 0 || strcmp(command, "exit") == 0) {
            client->receiving = 0;
            printf("👋 Até logo!\n");
            free(line);
            break;
        }
        else if (strcmp(command, "help") == 0) {
            print_help();
        }
        else if (strcmp(command, "login") == 0 && args >= 2) {
            login_user(client, arg1);
        }
        else if (strcmp(command, "users") == 0) {
            list_users(client);
        }
        else if (strcmp(command, "channel") == 0 && args >= 2) {
            create_channel(client, arg1);
        }
        else if (strcmp(command, "channels") == 0) {
            // Implementar list_channels
            printf("📢 Funcionalidade em desenvolvimento\n");
        }
        else if (strcmp(command, "pub") == 0 && args >= 3) {
            publish_message(client, arg1, arg2);
        }
        else if (strcmp(command, "msg") == 0 && args >= 3) {
            send_private_message(client, arg1, arg2);
        }
        else if (strcmp(command, "sub") == 0 && args >= 2) {
            char topic[64];
            snprintf(topic, sizeof(topic), "channel.%s", arg1);
            subscribe_to_topic(client, topic);
        }
        else if (strcmp(command, "unsub") == 0 && args >= 2) {
            char topic[64];
            snprintf(topic, sizeof(topic), "channel.%s", arg1);
            unsubscribe_from_topic(client, topic);
        }
        else {
            printf("❌ Comando desconhecido. Digite 'help' para ajuda.\n");
        }
        
        free(line);
    }
}

int main() {
    printf("🚀 Iniciando Cliente BBS em C...\n");
    
    bbs_client_t client;
    memset(&client, 0, sizeof(client));
    
    // Inicializar ZeroMQ
    client.context = zmq_ctx_new();
    client.req_socket = zmq_socket(client.context, ZMQ_REQ);
    client.sub_socket = zmq_socket(client.context, ZMQ_SUB);
    
    // Conectar sockets
    if (zmq_connect(client.req_socket, BROKER_ENDPOINT) != 0) {
        printf("❌ Erro ao conectar com broker\n");
        return 1;
    }
    
    if (zmq_connect(client.sub_socket, PUBSUB_ENDPOINT) != 0) {
        printf("❌ Erro ao conectar com pubsub\n");
        return 1;
    }
    
    printf("✅ Conectado ao sistema BBS\n");
    
    // Iniciar modo interativo
    start_interactive(&client);
    
    // Limpeza
    zmq_close(client.req_socket);
    zmq_close(client.sub_socket);
    zmq_ctx_destroy(client.context);
    
    return 0;
}