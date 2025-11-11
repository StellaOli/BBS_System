package common

import (
	"fmt"
	"time"

	"github.com/vmihailenco/msgpack/v5"
)

// Message types
const (
	ServiceRank      = "rank"
	ServiceList      = "list"
	ServiceHeartbeat = "heartbeat"
	ServiceClock     = "clock"
	ServiceElection  = "election"
)

// BaseMessage represents the common message structure
type BaseMessage struct {
	Service   string                 `msgpack:"service"`
	Data      map[string]interface{} `msgpack:"data"`
	Timestamp int64                  `msgpack:"timestamp,omitempty"`
	Clock     int64                  `msgpack:"clock,omitempty"`
}

// ClockMessage for clock synchronization
type ClockMessage struct {
	Time      int64 `msgpack:"time"`
	Timestamp int64 `msgpack:"timestamp"`
	Clock     int64 `msgpack:"clock"`
}

// ElectionMessage for leader election
type ElectionMessage struct {
	Election    string `msgpack:"election,omitempty"`
	Coordinator string `msgpack:"coordinator,omitempty"`
	Timestamp   int64  `msgpack:"timestamp"`
	Clock       int64  `msgpack:"clock"`
}

// ServerInfo represents server information
type ServerInfo struct {
	Name     string `msgpack:"name"`
	Rank     int    `msgpack:"rank"`
	LastSeen int64  `msgpack:"last_seen"`
}

// LogicalClock manages logical time
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

func (lc *LogicalClock) Set(value int64) {
	lc.clock = value
}

// Message packing utilities
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

func UnpackMessage(data []byte) (*BaseMessage, error) {
	var message BaseMessage
	err := msgpack.Unmarshal(data, &message)
	if err != nil {
		return nil, err
	}
	return &message, nil
}

// Create specific message types
func CreateRankMessage(serverName string, clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{
		"user": serverName,
	}
	return PackMessage(ServiceRank, data, clock)
}

func CreateListMessage(clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{}
	return PackMessage(ServiceList, data, clock)
}

func CreateHeartbeatMessage(serverName string, clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{
		"user": serverName,
	}
	return PackMessage(ServiceHeartbeat, data, clock)
}

func CreateClockMessage(clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{
		"time": time.Now().Unix(),
	}
	return PackMessage(ServiceClock, data, clock)
}

func CreateElectionMessage(clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{}
	return PackMessage(ServiceElection, data, clock)
}

func CreateCoordinatorMessage(coordinator string, clock *LogicalClock) ([]byte, error) {
	data := map[string]interface{}{
		"coordinator": coordinator,
	}
	return PackMessage(ServiceElection, data, clock)
}

// Extract fields from message data
func ExtractStringField(data map[string]interface{}, field string) string {
	if value, exists := data[field]; exists {
		if str, ok := value.(string); ok {
			return str
		}
	}
	return ""
}

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

// Print utilities for debugging
func PrintMessage(message *BaseMessage) {
	fmt.Printf("📨 Service: %s\n", message.Service)
	fmt.Printf("🕒 Timestamp: %d\n", message.Timestamp)
	fmt.Printf("⏰ Logical Clock: %d\n", message.Clock)
	fmt.Printf("📊 Data: %+v\n", message.Data)
}