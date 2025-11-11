package main

import (
	"log"
	"time"

	"github.com/pebbe/zmq4"
	"github.com/vmihailenco/msgpack/v5"
)

// ServerInfo representa informações do servidor
type ServerInfo struct {
	Name     string `msgpack:"name"`
	Rank     int    `msgpack:"rank"`
	LastSeen int64  `msgpack:"last_seen"`
}

// LogicalClock gerencia o tempo lógico
type LogicalClock struct {
	clock int64
}

func NewLogicalClock() *LogicalClock {
	return &LogicalClock{clock: 1}
}

func (lc *LogicalClock) Increment() int64 {
	lc.clock++
	return lc.clock
}

func (lc *LogicalClock) Update(receivedClock int64) int64 {
	if receivedClock > lc.clock {
		lc.clock = receivedClock + 1
	} else {
		lc.clock++
	}
	return lc.clock
}

func (lc *LogicalClock) Get() int64 {
	return lc.clock
}

// ReferenceServer gerencia servidores e ranks
type ReferenceServer struct {
	servers    map[string]*ServerInfo
	nextRank   int
	context    *zmq4.Context
	socket     *zmq4.Socket
	logicClock *LogicalClock
}

// NewReferenceServer cria novo servidor de referência
func NewReferenceServer() *ReferenceServer {
	context, _ := zmq4.NewContext()
	socket, _ := context.NewSocket(zmq4.REP)

	return &ReferenceServer{
		servers:    make(map[string]*ServerInfo),
		nextRank:   1,
		context:    context,
		socket:     socket,
		logicClock: NewLogicalClock(),
	}
}

// BaseMessage estrutura base das mensagens
type BaseMessage struct {
	Service   string                 `msgpack:"service"`
	Data      map[string]interface{} `msgpack:"data"`
	Timestamp int64                  `msgpack:"timestamp,omitempty"`
	Clock     int64                  `msgpack:"clock,omitempty"`
}

// handleRankRequest processa requisição de rank
func (rs *ReferenceServer) handleRankRequest(serverName string, clientClock int64) *BaseMessage {
	rs.logicClock.Update(clientClock)
	rs.logicClock.Increment()

	// Registrar ou atualizar servidor
	if server, exists := rs.servers[serverName]; exists {
		server.LastSeen = time.Now().Unix()
		log.Printf("🔄 Servidor %s atualizado (rank %d)", serverName, server.Rank)
	} else {
		rs.servers[serverName] = &ServerInfo{
			Name:     serverName,
			Rank:     rs.nextRank,
			LastSeen: time.Now().Unix(),
		}
		log.Printf("✅ Novo servidor registrado: %s (rank %d)", serverName, rs.nextRank)
		rs.nextRank++
	}

	return &BaseMessage{
		Service: "rank",
		Data: map[string]interface{}{
			"rank":      rs.servers[serverName].Rank,
			"timestamp": time.Now().Unix(),
			"clock":     rs.logicClock.Get(),
		},
		Timestamp: time.Now().Unix(),
		Clock:     rs.logicClock.Get(),
	}
}

// handleListRequest processa requisição de lista
func (rs *ReferenceServer) handleListRequest(clientClock int64) *BaseMessage {
	rs.logicClock.Update(clientClock)
	rs.logicClock.Increment()

	// Criar lista de servidores ativos (últimos 2 minutos)
	activeServers := make([]map[string]interface{}, 0)
	now := time.Now().Unix()
	
	for _, server := range rs.servers {
		if now-server.LastSeen < 120 { // 2 minutos
			activeServers = append(activeServers, map[string]interface{}{
				"name": server.Name,
				"rank": server.Rank,
			})
		}
	}

	log.Printf("📋 Lista de servidores solicitada: %d servidores ativos", len(activeServers))

	return &BaseMessage{
		Service: "list",
		Data: map[string]interface{}{
			"list":      activeServers,
			"timestamp": time.Now().Unix(),
			"clock":     rs.logicClock.Get(),
		},
		Timestamp: time.Now().Unix(),
		Clock:     rs.logicClock.Get(),
	}
}

// handleHeartbeat processa heartbeat
func (rs *ReferenceServer) handleHeartbeat(serverName string, clientClock int64) *BaseMessage {
	rs.logicClock.Update(clientClock)
	rs.logicClock.Increment()

	// Atualizar último seen se o servidor existir
	if server, exists := rs.servers[serverName]; exists {
		server.LastSeen = time.Now().Unix()
		log.Printf("💓 Heartbeat recebido de %s", serverName)
	} else {
		log.Printf("⚠️ Heartbeat de servidor não registrado: %s", serverName)
	}

	return &BaseMessage{
		Service: "heartbeat",
		Data: map[string]interface{}{
			"status":    "OK",
			"timestamp": time.Now().Unix(),
			"clock":     rs.logicClock.Get(),
		},
		Timestamp: time.Now().Unix(),
		Clock:     rs.logicClock.Get(),
	}
}

// handleClockRequest processa requisição de tempo
func (rs *ReferenceServer) handleClockRequest(clientClock int64) *BaseMessage {
	rs.logicClock.Update(clientClock)
	rs.logicClock.Increment()

	return &BaseMessage{
		Service: "clock",
		Data: map[string]interface{}{
			"time":      time.Now().Unix(),
			"timestamp": time.Now().Unix(),
			"clock":     rs.logicClock.Get(),
		},
		Timestamp: time.Now().Unix(),
		Clock:     rs.logicClock.Get(),
	}
}

// handleElectionRequest processa requisição de eleição
func (rs *ReferenceServer) handleElectionRequest(clientClock int64) *BaseMessage {
	rs.logicClock.Update(clientClock)
	rs.logicClock.Increment()

	return &BaseMessage{
		Service: "election",
		Data: map[string]interface{}{
			"election":  "OK",
			"timestamp": time.Now().Unix(),
			"clock":     rs.logicClock.Get(),
		},
		Timestamp: time.Now().Unix(),
		Clock:     rs.logicClock.Get(),
	}
}

// processMessage processa mensagens recebidas
func (rs *ReferenceServer) processMessage(msg []byte) []byte {
	var request BaseMessage
	err := msgpack.Unmarshal(msg, &request)
	if err != nil {
		log.Printf("❌ Erro ao decodificar mensagem: %v", err)
		errorMsg, _ := msgpack.Marshal(&BaseMessage{
			Service: "error",
			Data: map[string]interface{}{
				"error": "Invalid message format",
			},
		})
		return errorMsg
	}

	log.Printf("📨 Mensagem recebida - Serviço: %s, Clock: %d", request.Service, request.Clock)

	var response *BaseMessage
	clientClock := request.Clock

	switch request.Service {
	case "rank":
		serverName := extractString(request.Data, "user")
		if serverName == "" {
			response = &BaseMessage{
				Service: "error",
				Data:    map[string]interface{}{"error": "Missing user field"},
			}
		} else {
			response = rs.handleRankRequest(serverName, clientClock)
		}

	case "list":
		response = rs.handleListRequest(clientClock)

	case "heartbeat":
		serverName := extractString(request.Data, "user")
		if serverName == "" {
			response = &BaseMessage{
				Service: "error",
				Data:    map[string]interface{}{"error": "Missing user field"},
			}
		} else {
			response = rs.handleHeartbeat(serverName, clientClock)
		}

	case "clock":
		response = rs.handleClockRequest(clientClock)

	case "election":
		response = rs.handleElectionRequest(clientClock)

	default:
		response = &BaseMessage{
			Service: "error",
			Data:    map[string]interface{}{"error": "Unknown service: " + request.Service},
		}
	}

	responseBytes, err := msgpack.Marshal(response)
	if err != nil {
		log.Printf("❌ Erro ao codificar resposta: %v", err)
		errorMsg, _ := msgpack.Marshal(&BaseMessage{
			Service: "error",
			Data:    map[string]interface{}{"error": "Internal server error"},
		})
		return errorMsg
	}

	return responseBytes
}

// extractString extrai string de map
func extractString(data map[string]interface{}, key string) string {
	if value, exists := data[key]; exists {
		if str, ok := value.(string); ok {
			return str
		}
	}
	return ""
}

// cleanupInactiveServers remove servidores inativos
func (rs *ReferenceServer) cleanupInactiveServers() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		now := time.Now().Unix()
		inactiveCount := 0

		for name, server := range rs.servers {
			if now-server.LastSeen > 300 { // 5 minutos
				delete(rs.servers, name)
				inactiveCount++
				log.Printf("🗑️ Servidor removido por inatividade: %s", name)
			}
		}

		if inactiveCount > 0 {
			log.Printf("🧹 Limpeza concluída: %d servidores inativos removidos", inactiveCount)
		}
	}
}

// Start inicia o servidor de referência
func (rs *ReferenceServer) Start(port string) {
	endpoint := "tcp://*:" + port
	err := rs.socket.Bind(endpoint)
	if err != nil {
		log.Fatalf("❌ Erro ao bindar socket em %s: %v", endpoint, err)
	}

	log.Printf("🚀 Servidor de Referência GO rodando em %s", endpoint)
	log.Printf("⏰ Relógio lógico iniciado: %d", rs.logicClock.Get())

	// Iniciar limpeza de servidores inativos em goroutine
	go rs.cleanupInactiveServers()

	// Loop principal
	for {
		msg, err := rs.socket.RecvBytes(0)
		if err != nil {
			log.Printf("❌ Erro ao receber mensagem: %v", err)
			continue
		}

		response := rs.processMessage(msg)

		_, err = rs.socket.SendBytes(response, 0)
		if err != nil {
			log.Printf("❌ Erro ao enviar resposta: %v", err)
		}
	}
}

// getStats retorna estatísticas do servidor
func (rs *ReferenceServer) getStats() map[string]interface{} {
	activeCount := 0
	now := time.Now().Unix()

	for _, server := range rs.servers {
		if now-server.LastSeen < 120 {
			activeCount++
		}
	}

	return map[string]interface{}{
		"total_servers":    len(rs.servers),
		"active_servers":   activeCount,
		"next_rank":        rs.nextRank,
		"logical_clock":    rs.logicClock.Get(),
		"timestamp":        time.Now().Unix(),
	}
}

func main() {
	log.Println("🚀 Iniciando Servidor de Referência GO para Sistema BBS...")
	log.Println("📋 Serviços disponíveis: rank, list, heartbeat, clock, election")

	server := NewReferenceServer()

	// Log inicial de estatísticas
	stats := server.getStats()
	log.Printf("📊 Estatísticas iniciais: %+v", stats)

	// Iniciar servidor na porta 5559
	server.Start("5559")
}