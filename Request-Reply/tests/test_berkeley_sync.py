import sys
import os
import zmq
import time
from datetime import datetime

sys.path.append('/app')

def test_clock_synchronization():
    """Testa sincronização de relógio entre servidores"""
    print("🧪 TESTANDO SINCRONIZAÇÃO DE RELÓGIO")
    
    context = zmq.Context()
    
    try:
        # Testar comunicação de clock com um servidor
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.connect("tcp://servidor-1:5555")
        
        clock_request = {
            "service": "clock",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": 1
            }
        }
        
        socket.send_json(clock_request)
        response = socket.recv_json()
        
        assert response["service"] == "clock"
        assert "time" in response["data"]
        print("✅ Sincronização de relógio: OK")
        
    except Exception as e:
        print(f"❌ Sincronização de relógio: ERRO - {e}")
    finally:
        socket.close()

def test_election_communication():
    """Testa comunicação de eleição entre servidores"""
    print("🧪 TESTANDO COMUNICAÇÃO DE ELEIÇÃO")
    
    context = zmq.Context()
    
    try:
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.connect("tcp://servidor-1:5555")
        
        election_request = {
            "service": "election", 
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": 1
            }
        }
        
        socket.send_json(election_request)
        response = socket.recv_json()
        
        assert response["service"] == "election"
        assert response["data"]["election"] == "OK"
        print("✅ Comunicação de eleição: OK")
        
    except Exception as e:
        print(f"❌ Comunicação de eleição: ERRO - {e}")
    finally:
        socket.close()

def run_berkeley_tests():
    """Executa todos os testes de sincronização Berkeley"""
    print("=" * 60)
    print("🔄 TESTES DE SINCRONIZAÇÃO BERKELEY")
    print("=" * 60)
    
    test_clock_synchronization()
    test_election_communication()
    
    print("\n" + "=" * 60)
    print("🎉 TESTES BERKELEY CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    run_berkeley_tests()