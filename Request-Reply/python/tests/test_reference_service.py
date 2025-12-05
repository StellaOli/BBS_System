import sys
import os
import zmq
import time
from datetime import datetime

sys.path.append('/app')

def test_reference_rank_service():
    """Testa serviço de rank da referência"""
    print("🧪 TESTANDO SERVIÇO DE RANK")
    
    context = zmq.Context()
    
    try:
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.connect("tcp://reference:5559")
        
        # Testar requisição de rank
        rank_request = {
            "service": "rank",
            "data": {
                "user": "test_server",
                "timestamp": datetime.now().isoformat(),
                "clock": 1
            }
        }
        
        socket.send_json(rank_request)
        response = socket.recv_json()
        
        assert response["service"] == "rank"
        assert "rank" in response["data"]
        print(f"✅ Serviço de rank: OK (rank: {response['data']['rank']})")
        
    except Exception as e:
        print(f"❌ Serviço de rank: ERRO - {e}")
    finally:
        socket.close()

def test_reference_list_service():
    """Testa serviço de listagem de servidores"""
    print("🧪 TESTANDO SERVIÇO DE LISTAGEM")
    
    context = zmq.Context()
    
    try:
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.connect("tcp://reference:5559")
        
        list_request = {
            "service": "list", 
            "data": {
                "timestamp": datetime.now().isoformat(),
                "clock": 1
            }
        }
        
        socket.send_json(list_request)
        response = socket.recv_json()
        
        assert response["service"] == "list"
        assert "list" in response["data"]
        print("✅ Serviço de listagem: OK")
        
    except Exception as e:
        print(f"❌ Serviço de listagem: ERRO - {e}")
    finally:
        socket.close()

def test_reference_heartbeat():
    """Testa sistema de heartbeat"""
    print("🧪 TESTANDO HEARTBEAT")
    
    context = zmq.Context()
    
    try:
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.connect("tcp://reference:5559")
        
        heartbeat_request = {
            "service": "heartbeat",
            "data": {
                "user": "test_server",
                "timestamp": datetime.now().isoformat(),
                "clock": 1
            }
        }
        
        socket.send_json(heartbeat_request)
        response = socket.recv_json()
        
        assert response["service"] == "heartbeat"
        print("✅ Heartbeat: OK")
        
    except Exception as e:
        print(f"❌ Heartbeat: ERRO - {e}")
    finally:
        socket.close()

def run_reference_tests():
    """Executa todos os testes do serviço de referência"""
    print("=" * 60)
    print("🏷️ TESTES DO SERVIÇO DE REFERÊNCIA")
    print("=" * 60)
    
    test_reference_rank_service()
    test_reference_list_service() 
    test_reference_heartbeat()
    
    print("\n" + "=" * 60)
    print("🎉 TESTES DE REFERÊNCIA CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    run_reference_tests()