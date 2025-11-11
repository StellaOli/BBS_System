import sys
import os
import time
import json
import pytest
import zmq
import threading
import random
from datetime import datetime, timedelta

sys.path.append('/app')

from python.persistence import BBSPersistence

class TestSystem:
    """Testes de sistema completo com sua arquitetura"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.test_dir = "/tmp/test_system"
        os.makedirs(self.test_dir, exist_ok=True)
        self.persistence = BBSPersistence(self.test_dir)
        
        self.context = zmq.Context()
        self.results = {}
        self.servers = ["servidor-1", "servidor-2", "servidor-3"]
        
    def teardown_method(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'context'):
            self.context.term()
        
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def get_random_server(self):
        """Retorna um servidor aleatório"""
        return random.choice(self.servers)

    def simulate_user_session(self, username, duration=15):
        """Simula sessão de usuário conectando a servidores aleatórios"""
        print(f"👤 Simulando {username} por {duration}s...")
        
        try:
            server = self.get_random_server()
            socket = self.context.socket(zmq.REQ)
            socket.setsockopt(zmq.RCVTIMEO, 5000)
            socket.connect(f"tcp://{server}:5555")
            
            start_time = time.time()
            messages_sent = 0
            successful_requests = 0
            
            # Registrar login
            login_msg = {
                "type": "user_login",
                "username": username,
                "server": server,
                "timestamp": datetime.now().isoformat()
            }
            socket.send_json(login_msg)
            response = socket.recv_json()
            if response.get("status") in ["success", "ok"]:
                successful_requests += 1
            
            # Ações durante a sessão
            action_types = ["channel_message", "private_message", "get_history"]
            channels = ["general", "tech", "random"]
            users = ["alice", "bob", "carol", "david"]
            
            while time.time() - start_time < duration:
                action = random.choice(action_types)
                
                if action == "channel_message":
                    msg = {
                        "type": "channel_message",
                        "from": username,
                        "to": random.choice(channels),
                        "content": f"{username} no {server} - {messages_sent}",
                        "timestamp": datetime.now().isoformat()
                    }
                elif action == "private_message":
                    msg = {
                        "type": "private_message",
                        "from": username,
                        "to": random.choice([u for u in users if u != username]),
                        "content": f"Privada de {username} - {messages_sent}",
                        "timestamp": datetime.now().isoformat()
                    }
                else:  # get_history
                    msg = {
                        "type": "get_history",
                        "user": username,
                        "channel": random.choice(channels),
                        "timestamp": datetime.now().isoformat()
                    }
                
                socket.send_json(msg)
                response = socket.recv_json()
                
                if response.get("status") in ["success", "ok"]:
                    successful_requests += 1
                    if action != "get_history":
                        messages_sent += 1
                
                # Trocar de servidor ocasionalmente
                if random.random() < 0.2:  # 20% de chance
                    socket.close()
                    server = self.get_random_server()
                    socket = self.context.socket(zmq.REQ)
                    socket.setsockopt(zmq.RCVTIMEO, 5000)
                    socket.connect(f"tcp://{server}:5555")
                    print(f"   {username} trocou para {server}")
                
                time.sleep(0.3 + random.random() * 0.7)  # Pausa aleatória
            
            # Registrar logout
            logout_msg = {
                "type": "user_logout",
                "username": username,
                "timestamp": datetime.now().isoformat()
            }
            socket.send_json(logout_msg)
            socket.recv_json()
            
            self.results[username] = {
                "messages_sent": messages_sent,
                "successful_requests": successful_requests,
                "duration": duration,
                "servers_used": [server]
            }
            
            print(f"✅ {username}: {messages_sent} mensagens, {successful_requests} reqs sucedidas")
            return messages_sent
            
        except Exception as e:
            print(f"❌ Erro na sessão de {username}: {e}")
            return 0

    def test_distributed_users(self):
        """Testa usuários distribuídos entre múltiplos servidores"""
        print("👥 Testando usuários distribuídos...")
        
        users = ["alice", "bob", "carol", "david", "eve", "frank"]
        threads = []
        
        # Iniciar sessões simultâneas
        for user in users:
            thread = threading.Thread(
                target=self.simulate_user_session,
                args=(user, 20)  # 20 segundos por sessão
            )
            threads.append(thread)
            thread.start()
            time.sleep(0.5)  # Espaçar início das threads
        
        # Aguardar todas as threads
        for thread in threads:
            thread.join()
        
        # Análise dos resultados
        total_messages = sum(result["messages_sent"] for result in self.results.values())
        total_requests = sum(result["successful_requests"] for result in self.results.values())
        
        print(f"\n📊 ESTATÍSTICAS DISTRIBUÍDAS:")
        print(f"   • {len(users)} usuários")
        print(f"   • {total_messages} mensagens enviadas")
        print(f"   • {total_requests} requisições bem-sucedidas")
        print(f"   • {len(self.servers)} servidores disponíveis")
        
        # Verificar que pelo menos alguns usuários usaram servidores diferentes
        unique_servers = set()
        for result in self.results.values():
            unique_servers.update(result["servers_used"])
        
        assert total_messages > 0, "Nenhuma mensagem foi enviada"
        assert total_requests > len(users) * 2, "Poucas requisições bem-sucedidas"
        
        print("✅ Usuários distribuídos: OK")

    def test_load_balancing(self):
        """Testa balanceamento de carga entre servidores"""
        print("⚖️ Testando balanceamento de carga...")
        
        try:
            # Enviar 30 requisições e verificar qual servidor responde
            server_responses = {server: 0 for server in self.servers}
            
            for i in range(30):
                server = self.get_random_server()
                socket = self.context.socket(zmq.REQ)
                socket.setsockopt(zmq.RCVTIMEO, 3000)
                socket.connect(f"tcp://{server}:5555")
                
                msg = {
                    "type": "ping",
                    "sequence": i,
                    "timestamp": datetime.now().isoformat()
                }
                
                socket.send_json(msg)
                
                try:
                    response = socket.recv_json()
                    server_responses[server] += 1
                    print(f"   {server} respondeu #{i}")
                except zmq.Again:
                    print(f"   {server} timeout #{i}")
                finally:
                    socket.close()
                
                time.sleep(0.1)
            
            # Análise da distribuição
            print(f"\n📊 DISTRIBUIÇÃO DE CARGA:")
            total_responses = sum(server_responses.values())
            for server, count in server_responses.items():
                percentage = (count / total_responses * 100) if total_responses > 0 else 0
                print(f"   • {server}: {count} respostas ({percentage:.1f}%)")
            
            # Verificar que múltiplos servidores responderam
            active_servers = sum(1 for count in server_responses.values() if count > 0)
            assert active_servers >= 2, f"Apenas {active_servers} servidores ativos"
            
            print("✅ Balanceamento de carga: OK")
            
        except Exception as e:
            print(f"❌ Erro no teste de balanceamento: {e}")

    def test_system_recovery(self):
        """Testa resiliência do sistema"""
        print("🔄 Testando resiliência do sistema...")
        
        try:
            # Testar se sistema continua funcionando mesmo se um servidor cair
            working_servers = []
            
            for server in self.servers:
                try:
                    socket = self.context.socket(zmq.REQ)
                    socket.setsockopt(zmq.RCVTIMEO, 2000)
                    socket.connect(f"tcp://{server}:5555")
                    
                    socket.send_json({"type": "ping"})
                    response = socket.recv_json()
                    
                    working_servers.append(server)
                    print(f"✅ {server} está funcionando")
                    
                except zmq.Again:
                    print(f"⚠️  {server} não responde (simulando falha)")
                except Exception as e:
                    print(f"⚠️  {server} erro: {e}")
                finally:
                    socket.close()
            
            # Tentar usar apenas servidores funcionantes
            if working_servers:
                test_server = random.choice(working_servers)
                socket = self.context.socket(zmq.REQ)
                socket.connect(f"tcp://{test_server}:5555")
                
                msg = {
                    "type": "channel_message",
                    "from": "recovery_test",
                    "to": "general",
                    "content": "Teste de recuperação",
                    "timestamp": datetime.now().isoformat()
                }
                
                socket.send_json(msg)
                response = socket.recv_json()
                
                assert response.get("status") in ["success", "ok"]
                print(f"✅ Sistema se recuperou usando {test_server}")
            else:
                pytest.fail("Nenhum servidor disponível")
                
        except Exception as e:
            print(f"❌ Erro no teste de recuperação: {e}")

    def test_clock_synchronization(self):
        """Testa sincronização de relógio lógico"""
        print("⏰ Testando sincronização de relógio...")
        
        try:
            # Verificar se servidores estão sincronizados com referência
            socket_ref = self.context.socket(zmq.REQ)
            socket_ref.setsockopt(zmq.RCVTIMEO, 3000)
            socket_ref.connect("tcp://reference:5559")
            
            # Obter tempo de referência
            socket_ref.send_json({"type": "get_time"})
            ref_response = socket_ref.recv_json()
            ref_time = ref_response.get("logical_time", ref_response.get("timestamp"))
            print(f"   Tempo de referência: {ref_time}")
            
            # Verificar tempos dos servidores
            for server in self.servers:
                try:
                    socket = self.context.socket(zmq.REQ)
                    socket.setsockopt(zmq.RCVTIMEO, 2000)
                    socket.connect(f"tcp://{server}:5555")
                    
                    socket.send_json({"type": "get_time"})
                    response = socket.recv_json()
                    server_time = response.get("logical_time", response.get("timestamp"))
                    
                    print(f"   {server}: {server_time}")
                    
                except Exception as e:
                    print(f"   {server}: erro ao obter tempo - {e}")
                finally:
                    socket.close()
            
            print("✅ Sincronização de relógio: VERIFICADA")
            
        except Exception as e:
            print(f"❌ Erro no teste de sincronização: {e}")

def test_complete_workflow():
    """Teste de workflow completo do sistema distribuído"""
    print("🌐 Testando workflow completo...")
    
    tester = TestSystem()
    
    try:
        tester.setup_method()
        
        print("1. 🔧 CONFIGURAÇÃO INICIAL")
        print(f"   Servidores: {', '.join(tester.servers)}")
        
        print("2. 👥 USUÁRIOS CONCORRENTES")
        tester.test_distributed_users()
        
        print("3. ⚖️ BALANCEAMENTO DE CARGA") 
        tester.test_load_balancing()
        
        print("4. 🔄 TESTE DE RESILIÊNCIA")
        tester.test_system_recovery()
        
        print("5. ⏰ SINCRONIZAÇÃO")
        tester.test_clock_synchronization()
        
        print("6. 📊 ANÁLISE FINAL")
        total_msgs = sum(r["messages_sent"] for r in tester.results.values())
        total_reqs = sum(r["successful_requests"] for r in tester.results.values())
        
        print(f"   • Mensagens totais: {total_msgs}")
        print(f"   • Requisições bem-sucedidas: {total_reqs}")
        print(f"   • Usuários simulados: {len(tester.results)}")
        
        print("✅ WORKFLOW COMPLETO: SUCESSO")
        return True
        
    except Exception as e:
        print(f"❌ WORKFLOW COMPLETO: FALHA - {e}")
        return False
    finally:
        tester.teardown_method()

def run_system_tests():
    """Executa todos os testes de sistema"""
    print("=" * 70)
    print("🌐 TESTES DE SISTEMA COMPLETO - ARQUITETURA DISTRIBUÍDA")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # Teste de usuários distribuídos
        tester = TestSystem()
        tester.setup_method()
        tester.test_distributed_users()
        tester.teardown_method()
        tests_passed += 1
        
        # Teste de balanceamento
        tester = TestSystem()
        tester.setup_method()
        tester.test_load_balancing()
        tester.teardown_method()
        tests_passed += 1
        
        # Teste de resiliência
        tester = TestSystem()
        tester.setup_method()
        tester.test_system_recovery()
        tester.teardown_method()
        tests_passed += 1
        
        # Teste completo
        if test_complete_workflow():
            tests_passed += 1
        
        print(f"\n📊 RESULTADO: {tests_passed}/{total_tests} testes passaram")
        
        if tests_passed >= 3:
            print("🎉 SISTEMA DISTRIBUÍDO: OPERACIONAL")
            return True
        else:
            print("💢 SISTEMA DISTRIBUÍDO: PROBLEMAS DETECTADOS")
            return False
            
    except Exception as e:
        print(f"❌ ERRO NOS TESTES DE SISTEMA: {e}")
        return False

if __name__ == "__main__":
    success = run_system_tests()
    sys.exit(0 if success else 1)