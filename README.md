# 🚀 Sistema BBS Distribuído com Relógios Lógicos

Um sistema de Bulletin Board System (BBS) distribuído implementado em múltiplas linguagens (C, Python, Go) com sincronização de relógios lógicos e arquitetura tolerante a falhas.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Componentes](#componentes)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Guia de Comandos](#guia-de-comandos)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Protocolo de Comunicação](#protocolo-de-comunicação)
- [Monitoramento](#monitoramento)
- [Desenvolvimento](#desenvolvimento)
- [Solução de Problemas](#solução-de-problemas)

## 🎯 Visão Geral

Este projeto implementa um sistema BBS distribuído com as seguintes características:

- **Arquitetura Distribuída**: Múltiplos servidores balanceando carga
- **Comunicação Assíncrona**: Usando ZeroMQ e MessagePack
- **Relógios Lógicos**: Implementação do algoritmo de Lamport
- **Tolerância a Falhas**: Mecanismos de eleição de coordenador
- **Pub/Sub**: Sistema de mensagens em tempo real
- **Multi-linguagem**: Componentes em C, Python e Go

## 🏗️ Arquitetura do Sistema
````
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Cliente   │    │ Auto-Client │    │ Auto-Client │
│     C       │    │     C-1     │    │     C-2     │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
┌─────────────────────────────────────────────────┐
│                   BROKER ZMQ                    │
│              (Load Balancer)                    │
└─────────────────────────────────────────────────┘
       │                  │                  │
┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
│  Servidor   │    │  Servidor   │    │  Servidor   │
│   Python 1  │    │   Python 2  │    │   Python 3  │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
┌─────────────────────────────────────────────────┐
│              PROXY PUB/SUB ZMQ                  │
└─────────────────────────────────────────────────┘
       │                  │                  │
┌──────┴──────┐    ┌──────┴───────┐   ┌──────┴──────┐
│ Referência  │    │ Persistência │   │   Testes    │
│    Go       │    │   SQLite     │   │   Python    │
└─────────────┘    └──────────────┘   └─────────────┘
````
## ⚙️ Componentes

### 🖥️ Servidores Python (`servidor-1`, `servidor-2`, `servidor-3`)
- Processam requisições dos clientes
- Gerenciam usuários, canais e mensagens
- Implementam relógios lógicos
- Participam da eleição de coordenador

### 🔄 Broker ZMQ (`broker`)
- Balanceador de carga entre clientes e servidores
- Roteia mensagens usando padrão ROUTER/DEALER
- Porta 5555 (clientes) e 5556 (servidores)

### 📡 Proxy Pub/Sub (`pubsub-proxy`)
- Gerencia sistema de publicação/assinatura
- Distribui mensagens em tempo real
- Porta 5557 (publicação) e 5558 (assinatura)

### ⏰ Servidor de Referência Go (`reference`)
- Servidor de relógio lógico central
- Coordena sincronização entre servidores
- Gerencia ranks dos servidores
- Porta 5559

### 👤 Cliente C Interativo (`cliente-c`)
- Cliente interativo com interface de linha de comando
- Suporte a comandos em tempo real
- Implementa relógio lógico do lado do cliente

### 🤖 Auto-Clients C (`auto-client-c-1`, `auto-client-c-2`)
- Clientes automatizados para testes de carga
- Simulam comportamento de usuários reais
- Geram tráfego automático de mensagens

### 🧪 Ambiente de Testes (`testes`)
- Testes de integração e sistema
- Verificação da arquitetura distribuída
- Testes de carga e resiliência

## 📋 Pré-requisitos

- **Docker** e **Docker Compose**
- 4GB+ de RAM disponível
- Linux/macOS/Windows com WSL2

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/StellaOli/BBS_System.git
cd BBS_System
```

### 2. Execute o sistema completo
```bash
# Iniciar todos os serviços:
docker-compose up -d  

# Verificar status:
docker-compose ps  

# Ver logs em tempo real:
docker-compose logs -f
```
### 3. Aguarde a inicialização
```bash
# Aguarde todos os serviços ficarem healthy (≈30 segundos):
watch -n 5 'docker-compose ps'
```

### 4. Acesse o cliente interativo
```bash
docker exec -it cliente-c ./client
```
---

## ⌨️ Guia de Comandos

### 🧍‍♂️ Comandos do Cliente Interativo

**login <nome>**  
Função: Autentica um usuário no sistema  
Exemplo:
```bash
[desconectado | ⏰1]> login alice  
✅ Login realizado com sucesso | ⏰ Clock: 3
```

**help**  
Função: Mostra todos os comandos disponíveis  
Exemplo:
```bash
[alice | ⏰5]> help  
📋 Comandos disponíveis:  
- login <nome> - Fazer login com nome de usuário  
- users - Listar todos os usuários  
- channel <nome> - Criar um novo canal  
- channels - Listar todos os canais  
- pub <canal> <msg> - Publicar mensagem em canal  
- msg <user> <msg> - Enviar mensagem privada  
- sub <canal> - Inscrever em canal  
- unsub <canal> - Cancelar inscrição  
- history - Histórico de mensagens  
- clock - Mostrar relógio lógico atual  
- help - Mostrar esta ajuda  
- quit - Sair do programa  
```
**quit ou exit**  
Função: Encerra o cliente  
Exemplo:  
```bash
[alice | ⏰15]> quit  
👋 Até logo! | ⏰ Clock final: 15  
```

---

### 👥 Comandos de Gerenciamento de Usuários

**users**  
Função: Lista todos os usuários cadastrados no sistema  
Exemplo:  
```bash
[alice | ⏰7]> users  
👥 Usuários cadastrados | ⏰ Clock: 8  
- alice  
- bob  
- carol  
```

---

### 📢 Comandos de Canais

**channel <nome>**  
Função: Cria um novo canal de comunicação  
Exemplo:  
```bash
[alice | ⏰9]> channel geral  
✅ Canal 'geral' criado com sucesso | ⏰ Clock: 11  
```

**channels**  
Função: Lista todos os canais disponíveis  
Exemplo:  
```bash
[alice | ⏰12]> channels  
📢 Canais disponíveis | ⏰ Clock: 13  
- geral  
- tech  
- random  
```

**sub <canal>**  
Função: Inscreve o usuário em um canal  
Exemplo:  
```bash
[alice | ⏰14]> sub tech  
✅ Inscrito no tópico: channel.tech | ⏰ Clock: 15  
```

**unsub <canal>**  
Função: Cancela a inscrição em um canal  
Exemplo:  
```bash
[alice | ⏰20]> unsub tech  
✅ Inscrição cancelada do tópico: channel.tech | ⏰ Clock: 21  
```
---

### 💬 Comandos de Mensagens

**pub <canal> <mensagem>**  
Função: Publica uma mensagem em um canal  
Exemplo:  
```bash
[alice | ⏰16]> pub tech Olá pessoal da tecnologia!  
✅ Mensagem publicada com sucesso | ⏰ Clock: 18  
Usuários inscritos recebem: 📢 [tech] alice: Olá pessoal da tecnologia!
```

**msg <usuário> <mensagem>**  
Função: Envia uma mensagem privada para outro usuário  
Exemplo:  
```bash
[alice | ⏰22]> msg bob Ei, tudo bem?  
✅ Mensagem enviada com sucesso | ⏰ Clock: 24  
Destinatário recebe: 📩 [PRIVADO] alice: Ei, tudo bem?  
```
---

### ⚙️ Comandos do Sistema

**clock**  
Função: Mostra o valor atual do relógio lógico  
Exemplo: 
```bash
[alice | ⏰25]> clock  
⏰ Relógio lógico atual: 25  
```

**history**  
Função: Exibe o histórico de mensagens (em desenvolvimento)  
Exemplo:  
```bash
[alice | ⏰26]> history  
📢 Funcionalidade em desenvolvimento | ⏰ Clock: 27  
```

---

## 💻 Uso do Sistema

Sessão Completa de Exemplo:
```bash
[desconectado | ⏰1]> login carol  
✅ Login realizado com sucesso | ⏰ Clock: 3  

[carol | ⏰4]> users  
👥 Usuários cadastrados | ⏰ Clock: 5  
- alice  
- bob  
- carol  

[carol | ⏰6]> channel musica  
✅ Canal 'musica' criado com sucesso | ⏰ Clock: 8  

[carol | ⏰9]> sub geral  
✅ Inscrito no tópico: channel.geral | ⏰ Clock: 10  

[carol | ⏰11]> pub geral Olá a todos!  
✅ Mensagem publicada com sucesso | ⏰ Clock: 13  

📢 [geral] bob: Bem-vinda Carol! | ⏰ Clock: 15  

[carol | ⏰16]> msg bob Obrigada! | ⏰ Clock: 18  

[carol | ⏰19]> quit  
👋 Até logo! | ⏰ Clock final: 19  

```

---

## 📊 Monitoramento do Sistema
```bash

# Ver logs específicos:
- docker logs broker  
- docker logs servidor-1  
- docker logs reference  

# Estatísticas do sistema:
docker exec servidor-1 python -c "  
from persistence import BBSPersistence  
p = BBSPersistence()  
print(p.get_system_stats())  
"
```

---

## 🧪 Testes

**Testes de Integração**
```bash
- docker exec testes python tests/test_integration.py  
- docker exec testes python tests/test_system.py  

# Teste específico do broker
- docker exec testes python tests/test_broker.py  

# Testes de Carga
- docker logs auto-client-c-1  
- docker logs auto-client-c-2  

# Testes Manuais
docker exec testes python -c "  
import zmq  
context = zmq.Context()  
socket = context.socket(zmq.REQ)  
socket.connect('tcp://broker:5555')  
socket.send_string('PING')  
print('✅ Sistema operacional')  
"
```

---

## 📁 Estrutura do Projeto

Request-Reply/
├── c/                               # Componentes em C
│   ├── common/                      # Código compartilhado (headers, libs)
│   ├── Dockerfile_autoclient        # Dockerfile do cliente automatizado
│   ├── Dockerfile_cliente           # Dockerfile do cliente interativo
│   ├── MakeFile                     # Automação de build
│   ├── auto_client.c                # Cliente automatizado (gera carga)
│   └── client.c                     # Cliente interativo
│
├── go/                              # Componentes em Go
│   ├── clock/                       # Implementação de relógio lógico
│   ├── common/                      # Código compartilhado
│   ├── reference/                   # Servidor de referência em Go
│   └── Dockerfile_reference         # Dockerfile do servidor de referência
│
├── python/                          # Componentes em Python
│   ├── __pycache__/                 # Cache de bytecode
│   ├── common/                      # Código utilitário compartilhado
│   ├── data/                        # Dados persistentes (ex: SQLite)
│   ├── Dockerfile_broker            # Dockerfile do Broker ZMQ
│   ├── Dockerfile_servidor          # Dockerfile do servidor Python
│   ├── Dockerfile_testes            # Dockerfile do ambiente de testes
│   ├── broker.py                    # Broker ZMQ (Load Balancer)
│   ├── persistence.py               # Persistência (SQLite)
│   ├── pubsub_proxy.py              # Proxy PUB/SUB ZMQ
│   ├── servidor.py                  # Servidor principal BBS
│   └── tests/                       # Testes de integração e unidade
│       ├── all_tests.py
│       ├── test_integration.py
│       ├── test_persistence_pt1.py
│       ├── test_persistence_pt2.py
│       └── test_system.py
│
├── teste/  # Scripts e experimentos isolados
│   ├── Dockerfile_teste      # Dockerfile auxiliar de testes
│   └── all_tests.py             
│   ├── test_integration.py
│   ├── test_persistence_pt1.py
│   ├── test_persistence_pt2.py
│   └── test_system.py
├── docker-compose.yml               # Orquestração dos containers
└── README.md                        # Documentação principal
---

## 📡 Protocolo de Comunicação

**MessagePack**  
Todos os componentes usam MessagePack para serialização binária eficiente:
```bash
# Estrutura da mensagem:
{  
  "service": "login|publish|message|users|channel...",  
  "data": { ... },  
  "timestamp": "ISO-8601",  
  "clock": 123  
}

```

**Relógios Lógicos**  
Implementação do algoritmo de Lamport:
- Incremento local antes de enviar mensagens  
- Atualização ao receber mensagens: clock = max(local, recebido) + 1  
- Sincronização via servidor de referência  

Fluxo do Relógio Lógico:
- login: +2 incrementos (envio + recebimento)  
- pub/msg: +2 incrementos (envio + confirmação)  
- sub/unsub: +1 incremento (ação local)  
- Receber mensagem: +1 incremento + atualização  

---

## 📊 Monitoramento

Comandos úteis:
```bash

- docker-compose ps  
- watch -n 5 'docker stats --no-stream'  
- docker-compose logs --tail=50  
- docker network inspect bbs-distribuido_bbs-network  
```

Métricas do sistema:
- Usuários ativos: Persistidos em SQLite  
- Mensagens trocadas: Histórico completo  
- Relógios lógicos: Sincronizados entre componentes  
- Performance: Latência via timestamps  

---

## 🛠️ Desenvolvimento

**Adicionar Novo Serviço**
1. Adicione Dockerfile na pasta correspondente  
2. Atualize docker-compose.yml  
3. Implemente protocolo MessagePack  
4. Adicione testes de integração  

**Debugging**
```bash
# Shell em qualquer container
docker exec -it servidor-1 sh

# Logs detalhados com debug
docker-compose down
DEBUG=1 docker-compose up

# Teste de conectividade
docker run --rm --network bbs-distribuido_bbs-network \
  appropriate/curl curl http://broker:5555
```

---

## 🐛 Solução de Problemas

**Problemas Comuns**

Container não inicia:  
```bash
docker-compose down  
docker system prune -f  
docker-compose up -d  
```

Timeout nas conexões:  
Verifique `docker logs broker`  
Aumente timeouts nos clientes  

Relógios não sincronizam:  
Verifique `docker logs reference`  
Confirme conectividade de rede  

Mensagens não entregues:  
Verifique `docker logs pubsub-proxy`  
Confirme inscrições nos tópicos  

**Comandos de Diagnóstico**
```bash
# 1. Verificar se todos containers estão rodando
docker ps

# 2. Testar conectividade de rede
docker exec -it cliente-c ping broker
docker exec -it servidor-1 ping broker

# 3. Verificar logs em tempo real
docker logs -f broker

# 4. Testar cliente manualmente
docker exec -it cliente-c ./client

# 5. Verificar se há erros nos servidores
docker logs servidor-1
docker logs servidor-2
```
```bash
# Reconstruir tudo
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Aguardar inicialização
sleep 30

# Testar novamente
docker exec -it cliente-c ./client
```

---

Desenvolvido como projeto acadêmico de **Sistemas Distribuídos 🎓**  
Arquitetura distribuída • Relógios lógicos • Tolerância a falhas • Mensageria em tempo real  

---

Fork o projeto  
Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)  
Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)  
Push para a branch (`git push origin feature/AmazingFeature`)  
Abra um Pull Request  


