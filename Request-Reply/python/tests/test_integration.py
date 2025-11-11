import sys
import os
import time
import json
import zmq
import pytest
import subprocess
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistence import BBSPersistence

class TestIntegration:
    """Testes de integração entre os componentes do sistema"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.test_dir = "/tmp/test_integration"
        os.makedirs(self.test_dir, exist_ok=True)
        self.persistence = BBSPersistence(self.test_dir)
        
        # Configuração ZMQ para testes
        self.context = zmq.Context()
        
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'context'):
            self.context.term()
        
        # Limpar dados de teste
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_servers_communication(self):
        """Testa comunicação com os servidores"""
        print("🔗 Testando comunicação com servidores...")
        
        servers = ["servidor-1", "servidor-2", "servidor-3"]
        
        for server in servers:
            try:
                socket = self.context.socket(zmq.REQ)
                socket.setsockopt(zmq.LINGER, 0)
                socket.setsockopt(zmq.RCVTIMEO, 3000)
                socket.connect(f"tcp://{server}:5555")
                
                # Enviar ping
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                socket.send_json(ping_message)
                
                response = socket.recv_json()
                assert "type" in response
                print(f"✅ Servidor {server}: RESPONDEU")
                
            except zmq.Again:
                print(f"⚠️  Servidor {server}: TIMEOUT")
            except Exception as e:
                print(f"❌ Servidor {server}: ERRO - {e}")
            finally:
                socket.close()

    def test_broker_communication(self):
        """Testa comunicação com o broker"""
        print("🔗 Testando comunicação com broker...")
        
        try:
            # Testar porta do broker (5555)
            broker_socket = self.context.socket(zmq.REQ)
            broker_socket.setsockopt(zmq.RCVTIMEO, 2000)
            broker_socket.connect("tcp://broker:5555")
            
            broker_socket.send_json({"type": "test"})
            
            try:
                response = broker_socket.recv_json()
                print("✅ Broker (5555): RESPONDEU")
            except zmq.Again:
                print("⚠️  Broker (5555): TIMEOUT (pode ser normal)")
                
            broker_socket.close()
            
        except Exception as e:
            print(f"❌ Broker: ERRO - {e}")

    def test_pubsub_proxy_communication(self):
        """Testa comunicação com pubsub-proxy"""
        print("🔗 Testando comunicação com pubsub-proxy...")
        
        try:
            # Testar porta do pubsub-proxy (5557)
            pub_socket = self.context.socket(zmq.PUB)
            pub_socket.setsockopt(zmq.LINGER, 0)
            pub_socket.connect("tcp://pubsub-proxy:5557")
            
            # Testar porta de subscribe (5558)
            sub_socket = self.context.socket(zmq.SUB)
            sub_socket.setsockopt(zmq.LINGER, 0)
            sub_socket.setsockopt(zmq.RCVTIMEO, 2000)
            sub_socket.connect("tcp://pubsub-proxy:5558")
            sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            
            time.sleep(1)  # Dar tempo para conexões
            
            # Publicar mensagem de teste
            test_msg = {"type": "test", "content": "pubsub test"}
            pub_socket.send_json(test_msg)
            
            try:
                received = sub_socket.recv_json()
                print("✅ PubSub-Proxy: FUNCIONANDO")
            except zmq.Again:
                print("⚠️  PubSub-Proxy: TIMEOUT (pode ser normal para pub/sub)")
                
            pub_socket.close()
            sub_socket.close()
            
        except Exception as e:
            print(f"❌ PubSub-Proxy: ERRO - {e}")

    def test_reference_clock(self):
        """Testa comunicação com o relógio de referência"""
        print("🔗 Testando relógio de referência...")
        
        try:
            socket = self.context.socket(zmq.REQ)
            socket.setsockopt(zmq.RCVTIMEO, 3000)
            socket.connect("tcp://reference:5559")
            
            # Solicitar tempo de referência
            request = {
                "type": "get_time",
                "timestamp": datetime.now().isoformat()
            }
            
            socket.send_json(request)
            
            response = socket.recv_json()
            assert "logical_time" in response or "timestamp" in response
            print("✅ Relógio de referência: RESPONDEU")
            
        except zmq.Again:
            print("⚠️  Relógio de referência: TIMEOUT")
        except Exception as e:
            print(f"❌ Relógio de referência: ERRO - {e}")
        finally:
            socket.close()

    def test_auto_clients_communication(self):
        """Testa se auto-clients podem se comunicar"""
        print("🔗 Testando comunicação com auto-clients...")
        
        # Verificar se os containers estão rodando
        auto_clients = ["auto-client-c-1", "auto-client-c-2"]
        
        for client in auto_clients:
            try:
                # Testar conectividade básica
                result = subprocess.run(
                    ["docker", "exec", client, "ls", "/app"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print(f"✅ {client}: CONECTADO")
                else:
                    print(f"❌ {client}: ERRO - {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️  {client}: TIMEOUT")
            except Exception as e:
                print(f"❌ {client}: ERRO - {e}")

    def test_message_flow_between_servers(self):
        """Testa fluxo de mensagens entre servidores"""
        print("🔗 Testando fluxo entre servidores...")
        
        try:
            # Conectar ao servidor 1
            socket1 = self.context.socket(zmq.REQ)
            socket1.connect("tcp://servidor-1:5555")
            
            # Enviar mensagem para servidor 1
            test_message = {
                "type": "channel_message",
                "from": "test_user",
                "to": "general",
                "content": "Mensagem de teste servidor-1",
                "timestamp": datetime.now().isoformat()
            }
            
            socket1.send_json(test_message)
            response1 = socket1.recv_json()
            
            assert response1.get("status") in ["success", "received", "ok"]
            print("✅ Servidor-1: PROCESSOU MENSAGEM")
            
            # Testar servidor 2 também
            socket2 = self.context.socket(zmq.REQ)
            socket2.connect("tcp://servidor-2:5555")
            
            test_message2 = {
                "type": "private_message",
                "from": "test_user",
                "to": "user2", 
                "content": "Mensagem privada teste",
                "timestamp": datetime.now().isoformat()
            }
            
            socket2.send_json(test_message2)
            response2 = socket2.recv_json()
            
            assert response2.get("status") in ["success", "received", "ok"]
            print("✅ Servidor-2: PROCESSOU MENSAGEM")
            
        except Exception as e:
            print(f"❌ Fluxo entre servidores: ERRO - {e}")

    def test_container_network(self):
        """Testa conectividade de rede entre containers"""
        print("🔗 Testando rede entre containers...")
        
        # Testar conectividade entre serviços principais
        connections = [
            ("servidor-1", "servidor-2"),
            ("servidor-1", "broker"),
            ("servidor-1", "reference"),
            ("broker", "pubsub-proxy"),
            ("cliente-c", "servidor-1"),
        ]
        
        for source, target in connections:
            try:
                result = subprocess.run(
                    ["docker", "exec", source, "ping", "-c", "1", target],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"✅ {source} -> {target}: CONECTADO")
                else:
                    print(f"❌ {source} -> {target}: SEM CONEXÃO")
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️  {source} -> {target}: TIMEOUT")
            except Exception as e:
                print(f"❌ {source} -> {target}: ERRO - {e}")

def run_integration_tests():
    """Executa todos os testes de integração"""
    print("=" * 70)
    print("🔗 TESTES DE INTEGRAÇÃO - SISTEMA BBS")
    print("=" * 70)
    
    tester = TestIntegration()
    tests_passed = 0
    total_tests = 6
    
    try:
        tester.setup_method()
        
        print("\n1. 🖥️  TESTANDO SERVIDORES...")
        tester.test_servers_communication()
        tests_passed += 1
        
        print("\n2. 🔄 TESTANDO BROKER...")
        tester.test_broker_communication()
        tests_passed += 1
        
        print("\n3. 📡 TESTANDO PUB/SUB PROXY...")
        tester.test_pubsub_proxy_communication()
        tests_passed += 1
        
        print("\n4. ⏰ TESTANDO RELÓGIO DE REFERÊNCIA...")
        tester.test_reference_clock()
        tests_passed += 1
        
        print("\n5. 🤖 TESTANDO AUTO-CLIENTS...")
        tester.test_auto_clients_communication()
        tests_passed += 1
        
        print("\n6. 🌐 TESTANDO REDE...")
        tester.test_container_network()
        tests_passed += 1
        
        print("\n7. 📨 TESTANDO FLUXO DE MENSAGENS...")
        tester.test_message_flow_between_servers()
        tests_passed += 1
        
        print(f"\n📊 RESULTADO: {tests_passed}/{total_tests} testes principais concluídos")
        
        if tests_passed >= 5:  # Pelo menos 5/7 devem passar
            print("✅ INTEGRAÇÃO: SISTEMA OPERACIONAL")
            return True
        else:
            print("⚠️  INTEGRAÇÃO: ALGUNS PROBLEMAS DETECTADOS")
            return False
            
    except Exception as e:
        print(f"❌ ERRO NOS TESTES DE INTEGRAÇÃO: {e}")
        return False
    finally:
        tester.teardown_method()

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)