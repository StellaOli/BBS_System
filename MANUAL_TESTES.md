# 📖 Manual de Testes - Sistema BBS Distribuído

## 🎯 Índice

1. [Visão Geral](#visão-geral)
2. [Inicializar Sistema](#inicializar-sistema)
3. [Teste por Requisito](#teste-por-requisito)
   - [Parte 1: Request-Reply](#parte-1-request-reply)
   - [Parte 2: Pub/Sub](#parte-2-pubsub)
   - [Parte 3: MessagePack](#parte-3-messagepack)
   - [Parte 4: Relógios Lógicos e Eleição](#parte-4-relógios-lógicos-e-eleição)
   - [Parte 5: Replicação](#parte-5-replicação)
4. [Comandos Rápidos](#comandos-rápidos)

---

## 🚀 Visão Geral

Sistema BBS (Bulletin Board System) distribuído com:
- ✅ **3 servidores Python** (replicação Write-All/Read-Any)
- ✅ **1 servidor Go** (coordenação, eleição, sincronização)
- ✅ **Cliente interativo em C** (comunicação com relógio lógico)
- ✅ **2 bots automáticos em C** (teste contínuo)
- ✅ **Arquitetura ZeroMQ** (REQ-REP e XPUB-XSUB)
- ✅ **MessagePack** (serialização eficiente)

---

## 📦 Inicializar Sistema

### **1. Subir todos os containers**

```bash
cd /workspaces/codespaces-blank/Request-Reply
docker-compose up -d
sleep 3
```

### **2. Verificar status**

```bash
docker-compose ps
```

Esperado: 11 containers em estado `Up`

```
✔ reference (Go reference server)
✔ broker (Python REQ-REP)
✔ pubsub-proxy (Python XPUB-XSUB)
✔ servidor-1, servidor-2, servidor-3 (Python BBS)
✔ cliente-python (Cliente C interativo)
✔ auto-client-c-1, auto-client-c-2 (Bots)
✔ testes (Container auxiliar)
```

### **3. Entrar no cliente interativo**

```bash
docker-compose exec -T cliente-python ./client
```

---

## ✅ Teste por Requisito

### **PARTE 1: Request-Reply Pattern (ZeroMQ)**

#### Objetivo
Verificar que cliente consegue fazer requisições aos servidores através do broker (padrão REQ-REP).

#### Teste 1.1: Login Funcional

```bash
# No cliente interativo:
login usuario_teste
```

**Esperado:**
```
📥 Resposta recebida: 98 bytes | ⏰ Clock: XX
✅ Login realizado com sucesso | ⏰ Clock: XX
```

**Por trás dos panos:**
1. Cliente envia mensagem MessagePack ao broker (porta 5555)
2. Broker distribui round-robin entre 3 servidores (5556)
3. Servidor recebe, processa, incrementa relógio lógico
4. Resposta volta ao cliente

#### Teste 1.2: Listar Usuários

```bash
users
```

**Esperado:**
```
📥 Resposta recebida: XXX bytes | ⏰ Clock: XX
👥 Usuários cadastrados | ⏰ Clock: XX
  - usuario_teste
  - (outros usuários...)
```

#### Teste 1.3: Criar Canal

```bash
channel meu_canal
```

**Esperado:**
```
📥 Resposta recebida: 107 bytes | ⏰ Clock: XX
✅ Canal 'meu_canal' criado com sucesso | ⏰ Clock: XX
```

#### Verificação em Tempo Real

```bash
# Em outro terminal:
docker-compose logs -f broker | grep -i "round-robin\|distribuir"
docker-compose logs -f servidor-1 | grep -i "login\|channel"
```

---

### **PARTE 2: Pub/Sub Pattern (XPUB-XSUB)**

#### Objetivo
Verificar que mensagens publicadas em canais chegam aos subscribers através do proxy.

#### Teste 2.1: Publicar Mensagem

```bash
# No cliente:
pub meu_canal "Olá pessoal!"
```

**Esperado:**
```
📥 Resposta recebida: 94 bytes | ⏰ Clock: XX
✅  | ⏰ Clock: XX
```

#### Teste 2.2: Inscrever em Canal

```bash
sub meu_canal
```

**Esperado:**
```
✅ Inscrito no tópico: channel.meu_canal | ⏰ Clock: XX
```

#### Teste 2.3: Receber Mensagens Publicadas

Em outro terminal:

```bash
docker-compose exec -T cliente-python ./client

# Dentro do novo cliente:
login subscriber
sub meu_canal
# Aguarde... você verá mensagens publicadas em tempo real
```

#### Teste 2.4: Publicar Múltiplas Mensagens

```bash
pub meu_canal "Mensagem 1"
pub meu_canal "Mensagem 2"
pub meu_canal "Mensagem 3"
```

**Esperado:** Cada mensagem é confirmada com `✅`

#### Verificação em Tempo Real

```bash
docker-compose logs -f pubsub-proxy | grep -i "publicar\|mensagem"
docker-compose logs -f servidor-1 | grep -i "publish"
```

---

### **PARTE 3: MessagePack (Serialização)**

#### Objetivo
Verificar que mensagens são serializadas em binário eficiente (98 bytes vs ~150 JSON).

#### Teste 3.1: Observar Tamanho das Mensagens

```bash
# Toda resposta no cliente mostra:
# 📥 Resposta recebida: [BYTES] bytes
```

**Esperado:**
- Login: ~98 bytes
- Publicar: ~94 bytes
- Histórico: ~500+ bytes (várias mensagens)

Comparar com JSON:
```bash
# JSON seria ~1.5x maior
echo '{"service":"login","data":{"user":"teste","timestamp":"2025-12-04T02:30:00Z"},"clock":50}' | wc -c
# Resultado: ~110+ caracteres (MessagePack: 98 bytes)
```

#### Teste 3.2: Verificar Serialização em Arquivo

```bash
# Ver dados persistidos (JSON é apenas para persistência)
docker-compose exec servidor-1 cat /app/data/messages.json | head -20
```

**Esperado:** Estrutura JSON com campos: `id`, `type`, `from`, `to`, `content`, `timestamp`, `saved_at`

#### Verificação Técnica

```bash
# Ver size das respostas nos logs
docker-compose logs servidor-1 | grep "bytes"
```

---

### **PARTE 4: Relógios Lógicos e Eleição**

#### Objetivo
Verificar que cada operação incrementa o relógio lógico Lamport e que existe eleição de coordenador.

#### Teste 4.1: Incremento de Relógio Lógico

```bash
# No cliente:
login clock_test
# Observe: ⏰ Clock: 41

users
# Observe: ⏰ Clock: 43 (incrementou +2)

channel novo_canal
# Observe: ⏰ Clock: 45 (incrementou +2)

pub novo_canal "teste"
# Observe: ⏰ Clock: 47 (incrementou +2)

clock
# Mostra: ⏰ Relógio lógico atual: 47
```

**Esperado:** Cada operação incrementa o relógio lógico em +1 ou +2 (envio + recebimento).

#### Teste 4.2: Sincronização com Reference Server

```bash
# Ver heartbeats de todos os servidores
docker-compose logs reference | grep -i "heartbeat\|rank"
```

**Esperado:**
```
✅ Servidor servidor-1 registrado com rank 1
✅ Servidor servidor-2 registrado com rank 2
✅ Servidor servidor-3 registrado com rank 3
📍 Heartbeat recebido de servidor-1 (clock: XX)
📍 Heartbeat recebido de servidor-2 (clock: XX)
📍 Heartbeat recebido de servidor-3 (clock: XX)
```

#### Teste 4.3: Eleição de Coordenador ⭐

**Versão 1: Ver logs da eleição**

```bash
docker-compose logs reference | grep -i "eleição\|rank\|coordenador"
```

**Esperado:**
```
🗳️  Iniciando eleição - Servidor servidor-1 (rank 1)
🎖️ servidor-1 eleito como coordenador
📢 Coordenador servidor-1 anunciado
```

**Versão 2: Simular falha e novo coordenador**

```bash
# Terminal 1: Ver logs
docker-compose logs -f reference | grep -i "coordenador\|eleição"

# Terminal 2: Desligar servidor-1 (coordenador)
docker-compose stop servidor-1

# Aguarde 30 segundos...
# Esperado: Nova eleição e servidor-2 eleito
```

**Esperado na nova eleição:**
```
🗳️  Servidor servidor-2 (rank 2) iniciando eleição
🎖️ servidor-2 eleito como novo coordenador
📢 Coordenador servidor-2 anunciado
```

#### Teste 4.4: Ver Rank de cada Servidor

```bash
docker-compose logs servidor-1 | grep "Rank:"
docker-compose logs servidor-2 | grep "Rank:"
docker-compose logs servidor-3 | grep "Rank:"
```

**Esperado:**
```
🏆 Rank: 1 (servidor-1)
🏆 Rank: 2 (servidor-2)
🏆 Rank: 3 (servidor-3)
```

---

### **PARTE 5: Replicação (Write-All, Read-Any)**

#### Objetivo
Verificar que dados são replicados em todos 3 servidores e qualquer um consegue servir requisições.

#### Teste 5.1: Write-All - Dados em Todos os Servidores

```bash
# No cliente:
login replica_test
channel teste_replicado
pub teste_replicado "Mensagem replicada"
```

Verificar em todos os 3 servidores:

```bash
# Terminal 1:
docker-compose exec servidor-1 cat /app/data/channels.json | grep teste_replicado

# Terminal 2:
docker-compose exec servidor-2 cat /app/data/channels.json | grep teste_replicado

# Terminal 3:
docker-compose exec servidor-3 cat /app/data/channels.json | grep teste_replicado
```

**Esperado:** `teste_replicado` aparece em todas as 3 respostas.

#### Teste 5.2: Ver Operações Replicadas

```bash
docker-compose exec servidor-1 cat /app/data/messages.json | python3 -m json.tool | tail -20
docker-compose exec servidor-2 cat /app/data/messages.json | python3 -m json.tool | tail -20
docker-compose exec servidor-3 cat /app/data/messages.json | python3 -m json.tool | tail -20
```

**Esperado:** Mesmos dados em todos os 3 arquivos (últimas mensagens devem ser iguais).

#### Teste 5.3: Read-Any - Ler de Qualquer Servidor

```bash
# O broker distribui round-robin:
# Requisição 1 → servidor-1
# Requisição 2 → servidor-2
# Requisição 3 → servidor-3
# Requisição 4 → servidor-1 (volta ao começo)

# No cliente:
users   # → servidor-1
users   # → servidor-2
users   # → servidor-3
users   # → servidor-1 (de novo)
```

Ver distribuição:

```bash
docker-compose logs broker | grep "Distribuindo\|round-robin"
```

#### Teste 5.4: Falha e Recuperação

```bash
# Terminal 1: Ver operações replicadas
docker-compose logs -f servidor-1 | grep -i "operação\|replicação"

# Terminal 2: Desligar servidor-2
docker-compose stop servidor-2

# Terminal 3: Continuar usando o cliente
login durante_falha
channel novo_durante_falha

# Verificar que apenas servidor-1 e 3 têm os dados
docker-compose exec servidor-1 cat /app/data/channels.json | grep novo_durante_falha
docker-compose exec servidor-3 cat /app/data/channels.json | grep novo_durante_falha

# Restartar servidor-2
docker-compose up -d servidor-2
sleep 3

# Verificar que replicação restaurou dados
docker-compose exec servidor-2 cat /app/data/channels.json | grep novo_durante_falha
```

**Esperado:** Dados aparecem em todos os 3 servidores após reinicialização.

---

## 📋 Comandos Rápidos

### **Inicialização**

```bash
cd /workspaces/codespaces-blank/Request-Reply
docker-compose up -d
sleep 3
docker-compose exec -T cliente-python ./client
```

### **Teste Completo Automatizado**

```bash
cd /workspaces/codespaces-blank/Request-Reply

{
  # PARTE 1: Request-Reply
  echo "=== TESTE PARTE 1: REQUEST-REPLY ==="
  echo "login teste_automatico"
  sleep 1
  echo "users"
  sleep 1
  
  # PARTE 2: Pub/Sub
  echo "=== TESTE PARTE 2: PUB/SUB ==="
  echo "channel teste_auto"
  sleep 1
  echo "pub teste_auto 'Mensagem automática'"
  sleep 1
  
  # PARTE 4: Relógios Lógicos
  echo "=== TESTE PARTE 4: RELÓGIOS LÓGICOS ==="
  echo "clock"
  sleep 1
  
  # PARTE 5: Replicação
  echo "=== TESTE PARTE 5: REPLICAÇÃO ==="
  echo "history teste_auto"
  sleep 2
  
  echo "quit"
} | docker-compose exec -T cliente-python ./client
```

### **Observar Eleição (IMPORTANTE)**

```bash
# Terminal dedicado para eleição:
docker-compose logs -f reference | grep -E "Iniciando eleição|eleito como|rank|coordenador|Heartbeat"
```

### **Ver Logs por Componente**

```bash
# Broker (REQ-REP)
docker-compose logs -f broker

# Proxy (XPUB-XSUB)
docker-compose logs -f pubsub-proxy

# Servidor 1
docker-compose logs -f servidor-1

# Reference Server (Eleição)
docker-compose logs -f reference

# Auto-bots
docker-compose logs -f auto-client-c-1
docker-compose logs -f auto-client-c-2
```

### **Verificar Dados**

```bash
# Usuários cadastrados
docker-compose exec servidor-1 cat /app/data/users.json | python3 -m json.tool

# Canais criados
docker-compose exec servidor-1 cat /app/data/channels.json | python3 -m json.tool

# Histórico de logins
docker-compose exec servidor-1 cat /app/data/logins.json | python3 -m json.tool

# Todas as mensagens
docker-compose exec servidor-1 cat /app/data/messages.json | python3 -m json.tool | tail -30
```

### **Parar Sistema**

```bash
docker-compose down
```

---

## 🎯 Checklist de Validação

- [ ] **Parte 1**: REQ-REP funciona (login, criar canal, listar usuários)
- [ ] **Parte 2**: PUB-SUB funciona (publicar, inscrever, receber mensagens)
- [ ] **Parte 3**: MessagePack (mensagens ~98 bytes, não JSON)
- [ ] **Parte 4**: Relógios lógicos incrementam (clock mostra valor crescente)
- [ ] **Parte 4**: Eleição funciona (reference server elege coordenador)
- [ ] **Parte 5**: Replicação (dados em 3 servidores com Write-All/Read-Any)
- [ ] **Parte 5**: Falha e recuperação (servidor desligado recupera dados)

---

## 📞 Suporte Rápido

**P: Como entro no cliente?**
```bash
docker-compose exec -T cliente-python ./client
```

**P: Como vejo a eleição acontecendo?**
```bash
docker-compose logs -f reference | grep -i "eleição\|coordenador"
```

**P: Como verifico replicação?**
```bash
# Compare mensagens.json em todos os servidores
docker-compose exec servidor-1 cat /app/data/messages.json > /tmp/srv1.json
docker-compose exec servidor-2 cat /app/data/messages.json > /tmp/srv2.json
docker-compose exec servidor-3 cat /app/data/messages.json > /tmp/srv3.json
diff /tmp/srv1.json /tmp/srv2.json && echo "✅ Servidor 1 e 2 iguais"
```

**P: Como resetar dados?**
```bash
docker-compose down
docker volume prune -f
docker-compose up -d
```

---

**Data de criação:** 2025-12-04
**Versão:** 1.0 - Sistema Completo e Operacional ✅
