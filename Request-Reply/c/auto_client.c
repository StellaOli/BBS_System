#include <zmq.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <msgpack.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

#define BROKER_ENDPOINT "tcp://broker:5555"
#define PUBSUB_ENDPOINT "tcp://pubsub-proxy:5558"

typedef struct {
    void* context;
    void* req_socket;
    void* sub_socket;
    char username[32];
    int message_count;
    int running;
} auto_client_t;

// Incluir protocolo de mensagens
#include "common/message_protocol.h"

// Mensagens pré-definidas para os bots
const char* MESSAGES[] = {
    "Olá pessoal!",
    "Como vocês estão?",
    "Alguém online?",
    "Que dia lindo!",
    "Alguma novidade?",
    "Estou testando o sistema",
    "Funcionamento perfeito!",
    "Mensagem automática",
    "Hello world!",
    "Sistema BBS é ótimo!"
};
const int MESSAGE_COUNT = 10;

// Canais disponíveis
const char* CHANNELS[] = {"geral", "tech", "random", "offtopic", "testes"};
const int CHANNEL_COUNT = 5;

// Gerar nome de usuário aleatório
void generate_username(char* buffer, size_t size) {
    int random_num = rand() % 10000;
    snprintf(buffer, size, "bot_%04d", random_num);
}

// Função para enviar requisição usando MessagePack 
int send_request(auto_client_t* client, msgpack_sbuffer* request, msgpack_sbuffer* response) {
    // Enviar mensagem
    int send_result = zmq_send(client->req_socket, request->data, request->size, 0);
    if (send_result == -1) {
        printf("❌ Erro ao enviar mensagem: %s\n", strerror(errno));
        return -1;
    }

    // Receber resposta - usando zmq_recv com buffer
    char reply_buffer[4096];
    int recv_result = zmq_recv(client->req_socket, reply_buffer, sizeof(reply_buffer) - 1, 0);
    if (recv_result == -1) {
        printf("❌ Erro ao receber resposta: %s\n", strerror(errno));
        return -1;
    }

    // Copiar dados MessagePack para buffer de resposta
    msgpack_sbuffer_clear(response);
    msgpack_sbuffer_write(response, reply_buffer, recv_result);
    
    printf("📥 Resposta recebida: %d bytes\n", recv_result);
    return 0;
}

// Login do bot usando MessagePack
int bot_login(auto_client_t* client) {
    msgpack_sbuffer request_buf, response_buf;
    msgpack_sbuffer_init(&request_buf);
    msgpack_sbuffer_init(&response_buf);
    
    // ✅ USANDO MESSAGEPACK: Criar mensagem serializada
    create_login_message(client->username, &request_buf);
    
    if (send_request(client, &request_buf, &response_buf) != 0) {
        msgpack_sbuffer_destroy(&request_buf);
        msgpack_sbuffer_destroy(&response_buf);
        return -1;
    }
    
    // ✅ USANDO MESSAGEPACK: Parsear resposta serializada
    msgpack_object data;
    if (parse_message(response_buf.data, response_buf.size, &data) == 0) {
        char status[16] = "";
        char description[128] = "";
        
        extract_service_data(&data, status, sizeof(status), description, sizeof(description));
        
        if (strcmp(status, "sucesso") == 0) {
            printf("🤖 %s conectado\n", client->username);
            
            // Inscrever em alguns canais aleatórios
            for (int i = 0; i < 2; i++) {
                const char* channel = CHANNELS[rand() % CHANNEL_COUNT];
                char topic[64];
                snprintf(topic, sizeof(topic), "channel.%s", channel);
                zmq_setsockopt(client->sub_socket, ZMQ_SUBSCRIBE, topic, strlen(topic));
                printf("🤖 %s inscrito em: %s\n", client->username, channel);
            }
            
            msgpack_sbuffer_destroy(&request_buf);
            msgpack_sbuffer_destroy(&response_buf);
            return 0;
        }
    }
    
    msgpack_sbuffer_destroy(&request_buf);
    msgpack_sbuffer_destroy(&response_buf);
    return -1;
}

// Garantir que os canais existam usando MessagePack
void ensure_channels_exist(auto_client_t* client) {
    msgpack_sbuffer request_buf, response_buf;
    
    for (int i = 0; i < CHANNEL_COUNT; i++) {
        msgpack_sbuffer_init(&request_buf);
        msgpack_sbuffer_init(&response_buf);
        
        // ✅ USANDO MESSAGEPACK: Criar mensagem de canal
        create_channel_message(CHANNELS[i], &request_buf);
        
        if (send_request(client, &request_buf, &response_buf) == 0) {
            printf("🤖 Canal verificado: %s\n", CHANNELS[i]);
        }
        
        msgpack_sbuffer_destroy(&request_buf);
        msgpack_sbuffer_destroy(&response_buf);
    }
}

// Enviar mensagem aleatória usando MessagePack
void send_random_message(auto_client_t* client) {
    const char* channel = CHANNELS[rand() % CHANNEL_COUNT];
    const char* message = MESSAGES[rand() % MESSAGE_COUNT];
    
    msgpack_sbuffer request_buf, response_buf;
    msgpack_sbuffer_init(&request_buf);
    msgpack_sbuffer_init(&response_buf);
    
    // ✅ USANDO MESSAGEPACK: Criar mensagem de publicação serializada
    create_publish_message(client->username, channel, message, &request_buf);
    
    if (send_request(client, &request_buf, &response_buf) == 0) {
        printf("🤖 %s publicou em #%s: %s\n", client->username, channel, message);
        client->message_count++;
        
        // Mostrar tamanho da mensagem MessagePack (para demonstrar eficiência)
        printf("   📦 Tamanho MessagePack: %zu bytes\n", request_buf.size);
    }
    
    msgpack_sbuffer_destroy(&request_buf);
    msgpack_sbuffer_destroy(&response_buf);
}

// Thread para receber mensagens usando MessagePack
void* receive_messages(void* arg) {
    auto_client_t* client = (auto_client_t*)arg;
    
    while (client->running) {
        // ✅ CORREÇÃO: Usar buffer direto como na função send_request
        char msg_buffer[4096];
        
        // Timeout de 1 segundo
        int timeout_ms = 1000;
        zmq_setsockopt(client->sub_socket, ZMQ_RCVTIMEO, &timeout_ms, sizeof(timeout_ms));
        
        int recv_result = zmq_recv(client->sub_socket, msg_buffer, sizeof(msg_buffer) - 1, 0);
        if (recv_result != -1) {
            // ✅ USANDO MESSAGEPACK: Parsear mensagem Pub/Sub serializada
            msgpack_object data;
            if (parse_pubsub_message(msg_buffer, recv_result, &data) == 0) {
                char sender[32] = "Desconhecido";
                char content[256] = "";
                char target[32] = "";
                
                extract_string_field(&data, "sender", sender, sizeof(sender));
                extract_string_field(&data, "content", content, sizeof(content));
                extract_string_field(&data, "target", target, sizeof(target));
                
                // Ignorar próprias mensagens
                if (strcmp(sender, client->username) != 0) {
                    if (strncmp(target, "channel.", 8) == 0) {
                        printf("🤖 %s recebeu em #%s: %s: %s\n", 
                               client->username, target + 8, sender, content);
                    } else {
                        printf("🤖 %s recebeu privado: %s: %s\n", 
                               client->username, sender, content);
                    }
                }
            } else {
                printf("❌ Erro ao parsear mensagem Pub/Sub\n");
            }
        }
    }
    
    return NULL;
}

// Loop principal do bot
void run_bot(auto_client_t* client) {
    printf("🚀 Iniciando cliente automático: %s\n", client->username);
    printf("📦 Usando MessagePack para serialização binária\n");
    
    // Inicializar random seed
    srand(time(NULL) + (int)client->username[4]);
    
    // Conectar sockets
    client->context = zmq_ctx_new();
    if (!client->context) {
        printf("❌ %s: Erro ao criar contexto ZMQ\n", client->username);
        return;
    }
    
    client->req_socket = zmq_socket(client->context, ZMQ_REQ);
    client->sub_socket = zmq_socket(client->context, ZMQ_SUB);
    
    if (!client->req_socket || !client->sub_socket) {
        printf("❌ %s: Erro ao criar sockets\n", client->username);
        goto cleanup;
    }
    
    // Configurar timeout para requisições
    int timeout_ms = 5000; // 5 segundos
    zmq_setsockopt(client->req_socket, ZMQ_RCVTIMEO, &timeout_ms, sizeof(timeout_ms));
    
    if (zmq_connect(client->req_socket, BROKER_ENDPOINT) != 0) {
        printf("❌ %s: Erro ao conectar com broker\n", client->username);
        goto cleanup;
    }
    
    if (zmq_connect(client->sub_socket, PUBSUB_ENDPOINT) != 0) {
        printf("❌ %s: Erro ao conectar com pubsub\n", client->username);
        goto cleanup;
    }
    
    printf("✅ %s: Conectado ao sistema BBS\n", client->username);
    
    // Login
    if (bot_login(client) != 0) {
        printf("❌ %s: Falha no login\n", client->username);
        goto cleanup;
    }
    
    // Garantir canais
    ensure_channels_exist(client);
    
    // Iniciar thread de recebimento
    client->running = 1;
    pthread_t receive_thread;
    if (pthread_create(&receive_thread, NULL, receive_messages, client) != 0) {
        printf("❌ %s: Erro ao criar thread de recebimento\n", client->username);
        goto cleanup;
    }
    
    // Loop de envio de mensagens
    int messages_sent = 0;
    while (messages_sent < 10 && client->running) {
        // Espera entre 2 e 5 segundos
        int wait_time = 2 + (rand() % 4);
        sleep(wait_time);
        
        send_random_message(client);
        messages_sent++;
    }
    
    printf("✅ %s completou %d mensagens. Continuando a ouvir...\n", 
           client->username, messages_sent);
    
    // Manter recebendo mensagens
    while (client->running) {
        sleep(10);
    }
    
    // Aguardar thread terminar
    pthread_join(receive_thread, NULL);

cleanup:
    // Limpeza
    client->running = 0;
    
    if (client->req_socket) {
        zmq_close(client->req_socket);
    }
    if (client->sub_socket) {
        zmq_close(client->sub_socket);
    }
    if (client->context) {
        zmq_ctx_destroy(client->context);
    }
    
    printf("👋 %s finalizado\n", client->username);
}

int main(int argc, char* argv[]) {
    printf("🤖 Iniciando Cliente Automático BBS em C\n");
    printf("📦 Serialização: MessagePack (formato binário)\n");
    
    auto_client_t client;
    memset(&client, 0, sizeof(client));
    
    // Gerar username único
    generate_username(client.username, sizeof(client.username));
    
    // Executar bot
    run_bot(&client);
    
    return 0;
}