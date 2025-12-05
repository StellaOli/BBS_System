# 🎯 Sistema BBS Distribuído - Documentação

## 📌 O que é este projeto?

Sistema **Bulletin Board (BBS)** distribuído e replicado, implementando todos os padrões de sistemas distribuídos em produção:

- ✅ **Comunicação assíncrona** (Request-Reply + Pub-Sub via ZeroMQ)
- ✅ **Serialização eficiente** (MessagePack binário)
- ✅ **Sincronização de relógios** (Lamport Logical Clocks)
- ✅ **Eleição de coordenador** (algorithm-based)
- ✅ **Replicação de dados** (Write-All, Read-Any)
- ✅ **Tolerância a falhas** (recuperação automática)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────┐
│    REFERENCE SERVER (Go:5559)           │
│  Eleição, sincronização, coordenação    │
└─────────┬──────────────────────┬────────┘
          │                      │
     ┌────▼────┐            ┌───▼─────┐
     │ BROKER  │            │ XPUB/SUB│
     │ REQ-REP │            │ PROXY   │
     │5555-5556│            │5557-5558│
     └────┬────┘            └───┬─────┘
          │                     │
    ┌─────┼─────────────────────┼─────┐
    │     │                     │     │
  ┌─┴─┐ ┌─┴─┐ ┌──┐      ┌──────┴──┐ │
  │S-1│ │S-2│ │S-3│      │ Clientes │ │
  │   │ │   │ │   │      │ & Bots  │ │
  └───┘ └───┘ └──┘      └─────────┘ │
  (Servidores Python com replicação)  │
└──────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Iniciar o Sistema

```bash
cd /workspaces/codespaces-blank/Request-Reply
docker-compose up -d
sleep 3
```

### 2. Abrir Cliente Interativo

```bash
docker-compose exec -T cliente-c ./client
```

### 3. Testar Comandos Básicos

```
[desconectado]> login seu_nome
[seu_nome]> channels
[seu_nome]> channel novo_canal
[seu_nome]> pub novo_canal "Olá mundo!"
[seu_nome]> history novo_canal
[seu_nome]> quit
```

---

## 📖 Documentação Completa

**👉 [MANUAL DE TESTES DETALHADO](./MANUAL_TESTES.md)**

Inclui:
- ✅ Como testar cada requisito (Parte 1-5)
- ✅ Comandos para observar eleição
- ✅ Verificação de replicação
- ✅ Procedimento de falha e recuperação
- ✅ Análise de timestamps e relógios lógicos

---

## 📋 Comandos Principais

### Cliente Interativo

```bash
docker-compose exec -T cliente-c ./client
```

**Comandos disponíveis:**
```
login <nome>        # Fazer login
users              # Listar usuários
channels           # Listar canais
channel <nome>     # Criar canal
pub <canal> <msg>  # Publicar mensagem
msg <user> <msg>   # Mensagem privada
history <canal>    # Ver histórico
sub <canal>        # Inscrever em canal
unsub <canal>      # Cancelar inscrição
clock              # Ver relógio lógico
help               # Ajuda
quit               # Sair
```

---

## 📊 Monitorar Sistema

### Ver Logs em Tempo Real

```bash
# Eleição e coordenação
docker-compose logs -f reference | grep -i "eleição\|coordenador"

# Broker (REQ-REP)
docker-compose logs -f broker

# Servidor 1
docker-compose logs -f servidor-1
```

### Verificar Dados

```bash
# Mensagens armazenadas
docker-compose exec servidor-1 cat /app/data/messages.json | python3 -m json.tool

# Usuários cadastrados
docker-compose exec servidor-1 cat /app/data/users.json | python3 -m json.tool

# Canais criados
docker-compose exec servidor-1 cat /app/data/channels.json | python3 -m json.tool
```

### Testar Replicação

```bash
# Comparar dados em todos os 3 servidores
for i in 1 2 3; do
  echo "=== Servidor $i ==="
  docker-compose exec servidor-$i cat /app/data/messages.json | wc -l
done
```

---

## 🔍 Entender Cada Parte

### Parte 1: Request-Reply (ZeroMQ REQ-REP)
- **O que faz**: Comunicação síncrona cliente-servidor
- **Como testar**: `login usuario` → vê resposta do servidor
- **Verificar**: `docker-compose logs broker`

### Parte 2: Pub-Sub (ZeroMQ XPUB-XSUB)
- **O que faz**: Publicação em canais para múltiplos subscribers
- **Como testar**: `pub canal msg` + `sub canal` em outro cliente
- **Verificar**: `docker-compose logs pubsub-proxy`

### Parte 3: MessagePack
- **O que faz**: Serialização binária eficiente
- **Como testar**: Veja `📥 Resposta recebida: XX bytes` (98 bytes vs ~150 JSON)
- **Verificar**: Dados em `/app/data/*.json` após persistência

### Parte 4: Relógios Lógicos + Eleição
- **O que faz**: Ordenação causal de eventos + coordenação
- **Como testar**: `clock` mostra incremento; eleição em `docker-compose logs reference`
- **Verificar**: `docker-compose logs -f reference | grep -i "eleição"`

### Parte 5: Replicação
- **O que faz**: Dados replicados em 3 servidores (Write-All/Read-Any)
- **Como testar**: Compare `/app/data/` entre servidores
- **Verificar**: `docker-compose stop servidor-1` e dados ainda existem em 2 e 3

---

## 🛑 Parar Sistema

```bash
docker-compose down
```

**Para limpar dados:**
```bash
docker volume prune -f
```

---

## 📚 Estrutura de Arquivos

```
Request-Reply/
├── python/
│   ├── servidor.py          (3 servidores BBS)
│   ├── broker.py            (REQ-REP proxy)
│   ├── pubsub_proxy.py      (XPUB-XSUB proxy)
│   ├── persistence.py       (JSON persistence)
│   ├── replication.py       (Write-All/Read-Any)
│   └── data/
│       ├── users.json
│       ├── channels.json
│       ├── messages.json
│       └── logins.json
├── go/
│   └── reference/main.go    (Reference server)
├── c/
│   ├── client.c             (Cliente interativo)
│   ├── auto_client.c        (Bots automáticos)
│   └── common/
│       ├── message_protocol (MessagePack)
│       └── logical_clock    (Lamport clocks)
└── docker-compose.yml       (11 containers)
```

---

## ✅ Checklist de Validação

Antes de considerar pronto, execute:

- [ ] `login teste` → sucesso (Parte 1)
- [ ] `pub canal msg` → confirmado (Parte 2)
- [ ] Mensagem ~98 bytes (Parte 3)
- [ ] `clock` incrementa (Parte 4)
- [ ] Ver eleição: `docker-compose logs reference` (Parte 4)
- [ ] Dados em 3 servidores (Parte 5)

---

## 🎓 Referência Rápida

| Comando | Propósito |
|---------|----------|
| `docker-compose up -d` | Iniciar |
| `docker-compose ps` | Status |
| `docker-compose logs -f <service>` | Monitorar |
| `docker-compose exec servidor-1 cat /app/data/messages.json` | Ver dados |
| `docker-compose exec -T cliente-c ./client` | Cliente |
| `docker-compose down` | Parar |

---

**🎯 Para testes completos de cada requisito: [Veja MANUAL_TESTES.md](./MANUAL_TESTES.md)**

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                  REFERENCE SERVER (Go)                  │
│         Coordena ranks, heartbeat e sincronização       │
└─────────────────────────────────────────────────────────┘
         ↑ TCP:5559 (REQ-REP) ↑
         │                   │
    ┌────┴──────┐      ┌─────┴──────┐
    │ BROKER    │      │ PUBSUB     │
    │ REQ-REP   │      │ PROXY      │
    │ 5555-5556 │      │ 5557-5558  │
    └────┬──────┘      └─────┬──────┘
         │ TCP 5556          │ TCP 5558
         │                   │
    ┌────┴──────────────────────┬──────────────────────┐
    │                           │                      │
┌───┴────┐  ┌──────┐  ┌────────┴───┐  ┌───────────┐   │
│Servidor│  │ Serv │  │  Servidor  │  │   Clientes│   │
│   1    │  │  2   │  │     3      │  │   Bots    │   │
└────────┘  └──────┘  └────────────┘  └───────────┘   │
            (Replicação de dados entre servidores)      │
└──────────────────────────────────────────────────────┘
```

### Componentes

- **Broker (Python)**: Proxy REQ-REP com round-robin (porta 5555/5556)
- **Pub/Sub Proxy (Python)**: Proxy Publisher-Subscriber (porta 5557/5558)
- **Reference Server (Go)**: Gerencia ranks, eleição de coordenador, sincronização
- **Servidores (Python)**: 3 instâncias com replicação de dados
- **Clientes**: 
  - Cliente interativo Python
  - Bots automáticos Python (2 instâncias)
  - Cliente C (opcional)

## 🚀 Como Executar o Sistema

### Pré-requisitos

- **Docker** e **Docker Compose**
- **Python 3.9+** (para desenvolvimento local)
- **Go 1.18+** (para compilar Reference Server)
- **C compiler** (opcional, para cliente C)

### 1. Clonar o Repositório

```bash
cd /workspaces/codespaces-blank/Request-Reply
```

### 2. Iniciar o Sistema com Docker Compose

```bash
# Iniciar todos os containers
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f
```

**Saída esperada:**
```
✅ reference - Servidor de Referência rodando em tcp://*:5559
✅ broker - Broker BBS iniciado na porta 5555 (clientes) e 5556 (servidores)
✅ pubsub-proxy - Proxy Pub/Sub iniciado na porta 5557 (XSUB) e 5558 (XPUB)
✅ servidor-1, servidor-2, servidor-3 - Servidores BBS iniciados
✅ auto-client-py-1, auto-client-py-2 - Bots automáticos iniciados
```

### 3. Usar o Cliente Interativo

```bash
# Entrar no container do cliente Python
docker-compose exec cliente-python bash

# Ou rodar directamente
python client.py
```

**Exemplo de Sessão Interativa:**

```
🎯 Cliente BBS Interativo
Digite 'help' para ver o menu

==================================================
🔐 LOGIN NECESSÁRIO
==================================================

1. Login
0. Sair

➤ Escolha uma opção: 1
Nome de usuário: alice

🔐 Tentando login como 'alice'...
✅ Login realizado com sucesso!
   👤 Usuário: alice
   ⏰ Clock lógico: 1

👤 alice (Clock: 1)
📋 USUÁRIOS E CANAIS:
1. Listar usuários
2. Listar canais
3. Criar canal
4. Inscrever em canal
...

➤ Escolha uma opção: 2
📢 Solicitando lista de canais...
✅ Canais disponíveis: 4
   📌 general
   📌 announcements
   📌 dev
   📌 random

➤ Escolha uma opção: 5
Nome do canal: general
Mensagem: Olá a todos!

📤 Publicando no canal 'general'...
✅ Mensagem publicada no canal 'general'
```

### 4. Monitorar Bots Automáticos

```bash
# Ver logs dos bots
docker-compose logs auto-client-py-1 auto-client-py-2 -f

# Ver logs dos servidores (incluindo replicação)
docker-compose logs servidor-1 servidor-2 servidor-3 -f
```

### 5. Verificar Persistência de Dados

```bash
# Os dados são armazenados em JSON em /Request-Reply/python/data/
ls -la python/data/

# Ver usuários cadastrados
cat python/data/users.json

# Ver canais criados
cat python/data/channels.json

# Ver histórico de logins
cat python/data/logins.json

# Ver histórico de mensagens
cat python/data/messages.json
```

### 6. Parar o Sistema

```bash
# Parar todos os containers
docker-compose stop

# Remover containers e volumes
docker-compose down -v

# Ver status
docker-compose ps
```

## 📊 Testando o Sistema

### Executar Testes Unitários

```bash
# Entrar no container de testes
docker-compose exec testes bash

# Executar todos os testes
pytest -v tests/

# Executar teste específico
pytest -v tests/test_integration.py

# Com cobertura de código
pytest --cov=. tests/
```

### Testes Disponíveis

- `test_logical_clock.py` - Testa relógio lógico
- `test_persistence_pt1.py` - Testa persistência de usuários/canais
- `test_persistence_pt2.py` - Testa persistência de mensagens
- `test_berkeley_sync.py` - Testa sincronização Berkeley
- `test_reference_service.py` - Testa Reference Server
- `test_integration.py` - Teste de integração completo
- `test_system.py` - Teste de todo o sistema

## 🔧 Implementações por Parte

### Parte 1: Request-Reply

**Funcionalidades:**
- ✅ Login de usuários (sem senha)
- ✅ Listagem de usuários
- ✅ Criação de canais
- ✅ Listagem de canais
- ✅ Persistência em JSON (users.json, channels.json, logins.json)

**Formatos de Mensagem (MessagePack):**
```python
# Login Request
{
    "service": "login",
    "data": {
        "user": "alice",
        "clock": 1
    }
}

# Login Response
{
    "service": "login",
    "data": {
        "status": "success",
        "description": "Login realizado com sucesso"
    },
    "clock": 2
}
```

### Parte 2: Pub/Sub

**Funcionalidades:**
- ✅ Publicação em canais (XPUB/XSUB)
- ✅ Mensagens privadas entre usuários
- ✅ Inscrição em tópicos
- ✅ Cliente automático (bots) com publicação contínua
- ✅ Persistência de mensagens (messages.json)

**Formatos de Mensagem:**
```python
# Publicar em canal
{
    "service": "publish",
    "data": {
        "user": "alice",
        "channel": "general",
        "message": "Olá!"
    }
}

# Mensagem privada
{
    "service": "message",
    "data": {
        "src": "alice",
        "dst": "bob",
        "message": "Oi Bob!"
    }
}
```

### Parte 3: MessagePack

**Implementação:**
- ✅ Serialização binária com MessagePack (msgpack)
- ✅ Compatibilidade com Go e C
- ✅ Redução de tamanho de mensagens
- ✅ Suporte a int64 para timestamps e clocks

**Exemplo:**
```python
import msgpack

# Serializar
data = {"service": "login", "data": {"user": "alice"}, "clock": 1}
binary = msgpack.packb(data)

# Desserializar
original = msgpack.unpackb(binary)
```

### Parte 4: Relógios e Sincronização

**Componentes:**
- ✅ Relógio Lógico em todos os processos
- ✅ Reference Server (Go) - gerencia ranks e sincronização
- ✅ Heartbeat periódico (30s)
- ✅ Eleição de Coordenador (algoritmo Bully)
- ✅ Sincronização Berkeley (a cada 10 mensagens)

**Relógio Lógico:**
```python
class LogicalClock:
    def __init__(self):
        self.clock = 1
    
    def increment(self):
        self.clock += 1
        return self.clock
    
    def update(self, received_clock):
        self.clock = max(self.clock, received_clock) + 1
        return self.clock
```

**Serviços Reference Server:**

| Serviço | Descrição | Request | Response |
|---------|-----------|---------|----------|
| rank | Obter rank do servidor | {user: nome} | {rank: número} |
| list | Listar servidores | {} | {list: [...]} |
| heartbeat | Enviar heartbeat | {user: nome} | {status: OK} |
| clock | Sincronizar relógio | {} | {time: unix_time} |
| election | Requisição de eleição | {} | {election: OK} |

### Parte 5: Replicação de Dados

**Estratégia Implementada: Write-All, Read-Any**

- ✅ Todos os servidores replicam todos os dados
- ✅ Consistência eventual garantida
- ✅ Cada servidor copia dados dos outros via pull periódico
- ✅ Sincronização após cada operação de escrita

**Protocolo de Replicação:**
```python
# Cada servidor notifica os outros após escrever
{
    "service": "replicate",
    "data": {
        "operation": "add_user",
        "payload": {...},
        "timestamp": unix_time
    },
    "clock": valor_clock
}
```

**Garantias:**
- Durabilidade: Todos os dados persistem em disco (JSON)
- Consistência: Todos os servidores têm mesmos dados
- Disponibilidade: Sistema continua mesmo com 1 servidor down

## 📈 Monitoramento

### Ver Status do Sistema

```bash
# Verificar se todos os containers estão rodando
docker-compose ps

# Ver recursos utilizados
docker stats

# Inspecionar um container específico
docker inspect servidor-1

# Ver histórico de eventos
docker events --filter 'container=servidor-1'
```

### Logs Importantes

```bash
# Reference Server
docker-compose logs reference

# Broker
docker-compose logs broker

# Servidor específico
docker-compose logs servidor-1

# Cliente automático
docker-compose logs auto-client-py-1

# Seguir logs em tempo real
docker-compose logs -f
```

## 🐛 Troubleshooting

### Problema: Containers não iniciam

```bash
# Ver erro
docker-compose logs

# Reconstruir imagens
docker-compose build --no-cache

# Limpar e reiniciar
docker-compose down -v
docker-compose up -d
```

### Problema: Conexão recusada

```bash
# Verificar se porta está em uso
lsof -i :5555

# Ver rede do Docker
docker network inspect bbs-network

# Testar conexão entre containers
docker-compose exec broker nc -zv servidor-1 5556
```

### Problema: Dados não persistem

```bash
# Verificar permissões
ls -la python/data/
chmod 755 python/data/

# Verificar espaço em disco
df -h

# Reconstruir sem cache
docker-compose down -v
docker-compose up -d
```

## 📝 Estrutura de Arquivos

```
Request-Reply/
├── docker-compose.yml          # Orquestração de containers
├── python/
│   ├── broker.py              # Broker REQ-REP
│   ├── pubsub_proxy.py        # Proxy Pub/Sub
│   ├── servidor.py            # Servidor BBS
│   ├── client.py              # Cliente interativo (Novo!)
│   ├── auto_client.py         # Bot automático (Novo!)
│   ├── persistence.py         # Gerenciar persistência JSON
│   ├── common/
│   │   └── message_protocol.py # Protocolo MessagePack
│   ├── Dockerfile_broker      # Imagem broker
│   ├── Dockerfile_servidor    # Imagem servidor
│   ├── Dockerfile_testes      # Imagem testes
│   ├── data/                  # Dados persistidos (JSON)
│   │   ├── users.json
│   │   ├── channels.json
│   │   ├── logins.json
│   │   └── messages.json
│   └── tests/
│       ├── test_*.py          # Testes unitários e integração
│       └── all_tests.py       # Suite completa
├── go/
│   ├── reference/
│   │   └── main.go            # Reference Server (Novo!)
│   ├── common/
│   │   └── protocol.go        # Protocolo Go
│   ├── clock/
│   │   └── sync.go            # Sincronização Berkeley
│   ├── Dockerfile_reference   # Imagem Reference Server
│   └── go.sum
└── c/                         # Clientes em C (opcional)
    ├── client.c
    ├── auto_client.c
    └── common/
        ├── message_protocol.c
        └── logical_clock.c



