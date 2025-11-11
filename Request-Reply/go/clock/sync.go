package clock

import (
	"fmt"
	"log"
	"sort"
	"time"

	"github.com/pebbe/zmq4"
	"github.com/vmihailenco/msgpack/v5"
)

// Definições comuns (ou importar de um pacote common)
const (
	ServiceRank      = "rank"
	ServiceList      = "list"
	ServiceHeartbeat = "heartbeat"
	ServiceClock     = "clock"
	ServiceElection  = "election"
)

// BaseMessage representa a estrutura comum de mensagem
type BaseMessage struct {
	Service   string                 `msgpack:"service"`
	Data      map[string]interface{} `msgpack:"data"`
	Timestamp int64                  `msgpack:"timestamp,omitempty"`
	Clock     int64                  `msgpack:"clock,omitempty"`
}

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

// BerkeleyClock implementa o algoritmo Berkeley para sincronização de relógio
type BerkeleyClock struct {
	serverName    string
	rank          int
	coordinator   string
	isCoordinator bool
	logicalClock  *LogicalClock
	physicalClock int64
	offset        int64
	servers       []ServerInfo
	context       *zmq4.Context
	referenceURL  string
}

// ClockSyncResult representa o resultado da sincronização do relógio
type ClockSyncResult struct {
	Server    string
	Time      int64
	Offset    int64
	Timestamp int64
}

// NewBerkeleyClock cria um novo sincronizador de relógio Berkeley
func NewBerkeleyClock(serverName, referenceURL string) *BerkeleyClock {
	context, _ := zmq4.NewContext()
	
	return &BerkeleyClock{
		serverName:    serverName,
		referenceURL:  referenceURL,
		logicalClock:  NewLogicalClock(),
		physicalClock: time.Now().Unix(),
		context:       context,
		servers:       make([]ServerInfo, 0),
	}
}

// PackMessage empacota uma mensagem
func PackMessage(service string, data map[string]interface{}, clock *LogicalClock) ([]byte, error) {
	if clock != nil {
		clock.Increment()
	}
	
	message := BaseMessage{
		Service:   service,
		Data:      data,
		Timestamp: time.Now().Unix(),
		Clock:     clock.Get(),
	}
	
	return msgpack.Marshal(message)
}

// UnpackMessage desempacota uma mensagem
func UnpackMessage(data []byte) (*BaseMessage, error) {
	var message BaseMessage
	err := msgpack.Unmarshal(data, &message)
	if err != nil {
		return nil, err
	}
	return &message, nil
}

// ExtractStringField extrai campo string dos dados
func ExtractStringField(data map[string]interface{}, field string) string {
	if value, exists := data[field]; exists {
		if str, ok := value.(string); ok {
			return str
		}
	}
	return ""
}

// ExtractIntField extrai campo int dos dados
func ExtractIntField(data map[string]interface{}, field string) int64 {
	if value, exists := data[field]; exists {
		switch v := value.(type) {
		case int64:
			return v
		case int:
			return int64(v)
		case float64:
			return int64(v)
		}
	}
	return 0
}

// RegisterWithReference registra o servidor e obtém seu rank
func (bc *BerkeleyClock) RegisterWithReference() error {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	socket.Connect(bc.referenceURL)
	
	// Enviar requisição de rank
	data := map[string]interface{}{
		"user": bc.serverName,
	}
	message, err := PackMessage(ServiceRank, data, bc.logicalClock)
	if err != nil {
		return err
	}
	
	socket.SendBytes(message, 0)
	
	// Receber resposta
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return err
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return err
	}
	
	bc.rank = int(ExtractIntField(response.Data, "rank"))
	bc.logicalClock.Update(response.Clock)
	
	log.Printf("✅ Servidor %s registrado com rank %d", bc.serverName, bc.rank)
	return nil
}

// GetServerList recupera a lista de servidores disponíveis
func (bc *BerkeleyClock) GetServerList() error {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	socket.Connect(bc.referenceURL)
	
	data := map[string]interface{}{}
	message, err := PackMessage(ServiceList, data, bc.logicalClock)
	if err != nil {
		return err
	}
	
	socket.SendBytes(message, 0)
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return err
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return err
	}
	
	bc.logicalClock.Update(response.Clock)
	
	// Parse lista de servidores
	if list, exists := response.Data["list"]; exists {
		if serverList, ok := list.([]interface{}); ok {
			bc.servers = make([]ServerInfo, 0)
			for _, s := range serverList {
				if serverMap, ok := s.(map[string]interface{}); ok {
					server := ServerInfo{
						Name: ExtractStringField(serverMap, "name"),
						Rank: int(ExtractIntField(serverMap, "rank")),
					}
					bc.servers = append(bc.servers, server)
				}
			}
		}
	}
	
	log.Printf("📋 Lista de servidores atualizada: %d servidores", len(bc.servers))
	return nil
}

// SendHeartbeat envia heartbeat para o servidor de referência
func (bc *BerkeleyClock) SendHeartbeat() error {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	socket.Connect(bc.referenceURL)
	
	data := map[string]interface{}{
		"user": bc.serverName,
	}
	message, err := PackMessage(ServiceHeartbeat, data, bc.logicalClock)
	if err != nil {
		return err
	}
	
	socket.SendBytes(message, 0)
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return err
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return err
	}
	
	bc.logicalClock.Update(response.Clock)
	return nil
}

// SynchronizeClocks executa a sincronização do algoritmo Berkeley
func (bc *BerkeleyClock) SynchronizeClocks() (int64, error) {
	if !bc.isCoordinator {
		return bc.syncWithCoordinator()
	}
	
	return bc.coordinateSync()
}

// syncWithCoordinator sincroniza com o coordenador atual
func (bc *BerkeleyClock) syncWithCoordinator() (int64, error) {
	if bc.coordinator == "" {
		return 0, fmt.Errorf("nenhum coordenador definido")
	}
	
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	// Assume coordenador escutando na porta padrão + rank
	coordinatorURL := fmt.Sprintf("tcp://%s:556%d", bc.coordinator, bc.rank)
	socket.Connect(coordinatorURL)
	
	data := map[string]interface{}{
		"time": time.Now().Unix(),
	}
	message, err := PackMessage(ServiceClock, data, bc.logicalClock)
	if err != nil {
		return 0, err
	}
	
	socket.SendBytes(message, 0)
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return 0, err
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return 0, err
	}
	
	bc.logicalClock.Update(response.Clock)
	
	// Atualizar relógio físico com offset do coordenador
	coordinatorTime := ExtractIntField(response.Data, "time")
	currentTime := time.Now().Unix()
	bc.offset = coordinatorTime - currentTime
	bc.physicalClock = currentTime + bc.offset
	
	log.Printf("⏰ Sincronizado com coordenador %s. Offset: %d segundos", 
		bc.coordinator, bc.offset)
	
	return bc.offset, nil
}

// coordinateSync coordena a sincronização como coordenador
func (bc *BerkeleyClock) coordinateSync() (int64, error) {
	times := make([]ClockSyncResult, 0)
	
	// Coletar tempos de todos os servidores
	for _, server := range bc.servers {
		if server.Name == bc.serverName {
			// Pular próprio servidor
			continue
		}
		
		time, err := bc.getServerTime(server.Name)
		if err != nil {
			log.Printf("⚠️ Não foi possível obter tempo do servidor %s: %v", server.Name, err)
			continue
		}
		
		times = append(times, time)
	}
	
	// Adicionar tempo próprio do coordenador
	times = append(times, ClockSyncResult{
		Server:    bc.serverName,
		Time:      time.Now().Unix(),
		Offset:    0,
		Timestamp: time.Now().Unix(),
	})
	
	// Calcular tempo médio
	averageTime := bc.calculateAverageTime(times)
	
	// Calcular e enviar ajustes
	for _, result := range times {
		adjustment := averageTime - result.Time
		if result.Server != bc.serverName {
			bc.sendTimeAdjustment(result.Server, adjustment)
		} else {
			// Aplicar ajuste próprio
			bc.offset = adjustment
			bc.physicalClock = time.Now().Unix() + adjustment
		}
	}
	
	log.Printf("🎯 Sincronização Berkeley concluída. Tempo médio: %d, Ajuste aplicado: %d", 
		averageTime, bc.offset)
	
	return bc.offset, nil
}

// getServerTime obtém tempo de um servidor específico
func (bc *BerkeleyClock) getServerTime(serverName string) (ClockSyncResult, error) {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	serverURL := fmt.Sprintf("tcp://%s:5560", serverName) // Porta padrão
	socket.Connect(serverURL)
	
	data := map[string]interface{}{
		"time": time.Now().Unix(),
	}
	message, err := PackMessage(ServiceClock, data, bc.logicalClock)
	if err != nil {
		return ClockSyncResult{}, err
	}
	
	socket.SendBytes(message, 0)
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return ClockSyncResult{}, err
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return ClockSyncResult{}, err
	}
	
	bc.logicalClock.Update(response.Clock)
	
	return ClockSyncResult{
		Server:    serverName,
		Time:      ExtractIntField(response.Data, "time"),
		Timestamp: response.Timestamp,
	}, nil
}

// calculateAverageTime calcula o tempo médio de todos os servidores
func (bc *BerkeleyClock) calculateAverageTime(times []ClockSyncResult) int64 {
	if len(times) == 0 {
		return time.Now().Unix()
	}
	
	var sum int64
	for _, result := range times {
		sum += result.Time
	}
	
	return sum / int64(len(times))
}

// sendTimeAdjustment envia ajuste de tempo para um servidor
func (bc *BerkeleyClock) sendTimeAdjustment(serverName string, adjustment int64) {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	serverURL := fmt.Sprintf("tcp://%s:5561", serverName) // Porta de ajuste
	socket.Connect(serverURL)
	
	data := map[string]interface{}{
		"adjustment": adjustment,
		"timestamp":  time.Now().Unix(),
	}
	
	message, err := PackMessage("adjustment", data, bc.logicalClock)
	if err != nil {
		log.Printf("❌ Erro ao enviar ajuste para %s: %v", serverName, err)
		return
	}
	
	socket.SendBytes(message, 0)
	
	// Esperar por confirmação
	_, err = socket.RecvBytes(0)
	if err != nil {
		log.Printf("❌ Erro ao receber confirmação de %s: %v", serverName, err)
	}
}

// StartElection inicia um processo de eleição de líder
func (bc *BerkeleyClock) StartElection() error {
	log.Printf("🗳️ Iniciando eleição para servidor %s (rank %d)", bc.serverName, bc.rank)
	
	higherRankServers := bc.getHigherRankServers()
	
	if len(higherRankServers) == 0 {
		// Este servidor se torna coordenador
		bc.becomeCoordinator()
		return nil
	}
	
	// Enviar mensagens de eleição para servidores de rank maior
	for _, server := range higherRankServers {
		if bc.sendElectionMessage(server.Name) {
			// Se algum servidor de rank maior responder, esperar anúncio do coordenador
			return nil
		}
	}
	
	// Nenhum servidor de rank maior respondeu, tornar-se coordenador
	bc.becomeCoordinator()
	return nil
}

// getHigherRankServers retorna servidores com rank maior
func (bc *BerkeleyClock) getHigherRankServers() []ServerInfo {
	higher := make([]ServerInfo, 0)
	for _, server := range bc.servers {
		if server.Rank > bc.rank {
			higher = append(higher, server)
		}
	}
	
	// Ordenar por rank (decrescente)
	sort.Slice(higher, func(i, j int) bool {
		return higher[i].Rank > higher[j].Rank
	})
	
	return higher
}

// sendElectionMessage envia mensagem de eleição para um servidor
func (bc *BerkeleyClock) sendElectionMessage(serverName string) bool {
	socket, _ := bc.context.NewSocket(zmq4.REQ)
	defer socket.Close()
	
	serverURL := fmt.Sprintf("tcp://%s:5562", serverName) // Porta de eleição
	socket.Connect(serverURL)
	socket.SetRcvtimeo(5000) // Timeout de 5 segundos
	
	data := map[string]interface{}{}
	message, err := PackMessage(ServiceElection, data, bc.logicalClock)
	if err != nil {
		return false
	}
	
	socket.SendBytes(message, 0)
	reply, err := socket.RecvBytes(0)
	if err != nil {
		return false
	}
	
	response, err := UnpackMessage(reply)
	if err != nil {
		return false
	}
	
	bc.logicalClock.Update(response.Clock)
	return ExtractStringField(response.Data, "election") == "OK"
}

// becomeCoordinator torna este servidor o coordenador
func (bc *BerkeleyClock) becomeCoordinator() {
	bc.isCoordinator = true
	bc.coordinator = bc.serverName
	
	log.Printf("🎖️ Servidor %s eleito como coordenador", bc.serverName)
	
	// Anunciar coordenador para todos os servidores
	bc.announceCoordinator()
}

// announceCoordinator anuncia este servidor como coordenador para todos os servidores
func (bc *BerkeleyClock) announceCoordinator() {
	pubSocket, _ := bc.context.NewSocket(zmq4.PUB)
	defer pubSocket.Close()
	
	pubSocket.Bind("tcp://*:5563") // Porta de anúncio do coordenador
	
	data := map[string]interface{}{
		"coordinator": bc.serverName,
	}
	message, err := PackMessage(ServiceElection, data, bc.logicalClock)
	if err != nil {
		log.Printf("❌ Erro ao anunciar coordenador: %v", err)
		return
	}
	
	pubSocket.SendBytes(message, 0)
	log.Printf("📢 Coordenador %s anunciado para todos os servidores", bc.serverName)
}

// GetCurrentTime retorna o tempo atual sincronizado
func (bc *BerkeleyClock) GetCurrentTime() int64 {
	return time.Now().Unix() + bc.offset
}

// GetLogicalClock retorna o valor do relógio lógico
func (bc *BerkeleyClock) GetLogicalClock() int64 {
	return bc.logicalClock.Get()
}

// SetCoordinator define o coordenador atual
func (bc *BerkeleyClock) SetCoordinator(coordinator string) {
	bc.coordinator = coordinator
	bc.isCoordinator = (coordinator == bc.serverName)
}

// StartBackgroundTasks inicia tarefas em segundo plano
func (bc *BerkeleyClock) StartBackgroundTasks() {
	// Heartbeat a cada 30 segundos
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()
		
		for range ticker.C {
			bc.SendHeartbeat()
		}
	}()
	
	// Sincronizar a cada 2 minutos
	go func() {
		ticker := time.NewTicker(2 * time.Minute)
		defer ticker.Stop()
		
		for range ticker.C {
			bc.SynchronizeClocks()
		}
	}()
	
	// Atualizar lista de servidores a cada minuto
	go func() {
		ticker := time.NewTicker(1 * time.Minute)
		defer ticker.Stop()
		
		for range ticker.C {
			bc.GetServerList()
		}
	}()
}