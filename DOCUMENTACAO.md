# 📚 Índice de Documentação - Sistema BBS Distribuído

## 🎯 Seu projeto está completo! Aqui está como usar a documentação:

### 📖 **[MANUAL_TESTES.md](./MANUAL_TESTES.md)** ⭐ LEIA ISTO PRIMEIRO

**O que é:** Guia passo a passo para testar TODO o sistema

**Contém:**
- ✅ Como iniciar o sistema (3 passos)
- ✅ Testes para CADA REQUISITO (Parte 1-5)
- ✅ **Como observar a eleição funcionando** 🎯
- ✅ Testes de replicação
- ✅ Procedimento de falha/recuperação
- ✅ Comandos para conferir timestamps
- ✅ Checklist de validação

**Quando usar:** Quando você quer testar cada parte do sistema
**Tempo:** ~30 minutos para teste completo

---

### 📋 **[README.md](./README.md)** - Visão Geral Rápida

**O que é:** Documentação geral do projeto

**Contém:**
- 🎯 O que é o projeto
- 🏗️ Arquitetura
- 🚀 Quick Start (5 minutos)
- 📊 Como monitorar
- 🔍 Explicação de cada parte
- 📚 Estrutura de arquivos

**Quando usar:** Quando você quer entender o projeto em 5 minutos
**Tempo:** ~5 minutos para quick start

---

## 🚀 Quick Start (Copie e Cole)

### 1. Iniciar Sistema
```bash
cd /workspaces/codespaces-blank/Request-Reply
docker-compose up -d
sleep 3
```

### 2. Entrar no Cliente
```bash
docker-compose exec -T cliente-c ./client
```

### 3. Testar Comandos
```
login seu_nome
channels
channel novo_canal
pub novo_canal "Olá!"
history novo_canal
quit
```

---

## 🔍 Encontrar Informação Rápida

| Você quer... | Arquivo | Seção |
|---|---|---|
| Testar Parte 1 (Request-Reply) | MANUAL_TESTES | PARTE 1 |
| Testar Parte 2 (Pub-Sub) | MANUAL_TESTES | PARTE 2 |
| Ver eleição funcionando ⭐ | MANUAL_TESTES | PARTE 4.3 |
| Ver replicação funcionando | MANUAL_TESTES | PARTE 5 |
| Conferir timestamps | MANUAL_TESTES | Início |
| Entender arquitetura | README | Seção Arquitetura |
| Listar todos os comandos | README | Seção Comandos |
| Ver como monitorar | README | Seção Monitorar |

---

## ⭐ Comando MAIS IMPORTANTE - Ver Eleição

Para ver a eleição de coordenador funcionando em tempo real:

```bash
# Terminal 1: Ver a eleição
docker-compose logs -f reference | grep -i "eleição\|coordenador\|rank"

# Terminal 2: Usar o cliente
docker-compose exec -T cliente-c ./client
```

**Veja em MANUAL_TESTES.md → PARTE 4 → Teste 4.3 para detalhes completos**

---

## 📊 Estrutura Geral

```
/workspaces/codespaces-blank/
├── DOCUMENTACAO.md  ← Você está aqui
├── README.md  ← Visão geral rápida
├── MANUAL_TESTES.md  ← Testes passo a passo ⭐
│
└── Request-Reply/
    ├── docker-compose.yml  (11 containers)
    ├── python/  (3 servidores, broker, proxy)
    ├── go/  (Reference server)
    ├── c/  (Cliente C interativo + bots)
    └── data/  (JSON persistence)
```

---

## ✅ Checklist de Uso

- [ ] Li **MANUAL_TESTES.md** (para testar)
- [ ] Li **README.md** (para entender)
- [ ] Executei Quick Start
- [ ] Vi eleição funcionando
- [ ] Testei cada Parte (1-5)
- [ ] Verifiquei replicação
- [ ] Conferir timestamps

---

## 🎯 Próximos Passos

### Opção 1: Teste Rápido (5 min)
1. Abra **README.md**
2. Siga **Quick Start**
3. Pronto!

### Opção 2: Teste Completo (30 min)
1. Abra **MANUAL_TESTES.md**
2. Siga **Teste por Requisito**
3. Complete todo o checklist

### Opção 3: Ver Eleição (10 min)
1. Abra **MANUAL_TESTES.md**
2. Vá para **PARTE 4 → Teste 4.3**
3. Siga as instruções para ver eleição em tempo real

---

## 📞 Dúvidas Comuns

**P: Por onde começo?**  
R: Leia o **README.md** primeiro (5 min), depois **MANUAL_TESTES.md** para testes

**P: Como vejo a eleição funcionando?**  
R: Vá para **MANUAL_TESTES.md → PARTE 4 → Teste 4.3**

**P: Como vejo timestamps?**  
R: Vá para **MANUAL_TESTES.md → Teste 4.1** para relógios lógicos

**P: Como verifico replicação?**  
R: Vá para **MANUAL_TESTES.md → PARTE 5**

**P: Qual comando devo executar primeiro?**  
R: `cd /workspaces/codespaces-blank/Request-Reply && docker-compose up -d`

---

## 🎓 Estrutura de Aprendizado Recomendado

**Dia 1:**
1. Leia README.md (5 min)
2. Execute Quick Start (5 min)
3. Teste Parte 1 - Request-Reply (5 min)
4. Teste Parte 2 - Pub-Sub (5 min)

**Dia 2:**
1. Teste Parte 3 - MessagePack (5 min)
2. Teste Parte 4 - Relógios (10 min)
3. **Veja Eleição acontecendo** (10 min)
4. Teste Parte 5 - Replicação (15 min)

---

**Documentação Completa e Pronta! ✅**

Versão: 1.0  
Data: 2025-12-05  
Status: Sistema Operacional
