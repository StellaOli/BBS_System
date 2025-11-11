import zmq
import sys
import os
import threading
import time
from datetime import datetime

sys.path.append('/app')

class LogicalClock:
    """✅ NOVO: Relógio lógico para sincronização"""
    def __init__(self):
        self.clock = 1
    
    def increment(self):
        self.clock += 1
        return self.clock
    
    def update(self, received_clock):
        self.clock = max(self.clock, received_clock) + 1
        return self.clock
    
    def get(self):
        return self.clock

class BBSServer:
    def __init__(self, server_name="servidor-1"):
        self.context = zmq.Context()
        self.server_name = server_name
        
        # ✅ NOVO: Relógio lógico
        self.logical_clock = LogicalClock()
        
        # Socket REQ-REP (existente)
        self.rep_socket = self.context.socket(zmq.REP)
        
        # Socket PUB para publicar mensagens
        self.pub_socket = self.context.socket(zmq.PUB)
        
        # ✅ NOVO: Socket para comunicação com reference server
        self.ref_socket = self.context.socket(zmq.REQ)
        
        # ✅ NOVO: Socket para eleição e sincronização entre servidores
        self.election_socket = self.context.socket(zmq.REP)
        self.coordinator_socket = self.context.socket(zmq.REQ)
        
        from persistence import BBSPersistence
        from common.message_protocol import MessageProtocol
        
        self.persistence = BBSPersistence()
        self.MessageProtocol = MessageProtocol
        self.active_users = set()
        
        # ✅ NOVO: Variáveis para coordenação
        self.coordinator = None
        self.rank = None
        self.reference_endpoint = os.getenv('REFERENCE_ENDPOINT', 'tcp://reference:5559')
        self.running = True
    
    def register_with_reference(self):
        """✅ NOVO: Registrar servidor no reference server"""
        try:
            self.ref_socket.connect(self.reference_endpoint)
            
            # Enviar mensagem de rank
            rank_message = self.MessageProtocol.create_rank_message(
                self.server_name, 
                self.logical_clock.get()
            )
            self.ref_socket.send_string(rank_message)
            
            # Receber resposta
            response_str = self.ref_socket.recv_string()
            response = self.MessageProtocol.parse_message(response_str)
            
            # Atualizar relógio lógico
            received_clock = response.get("data", {}).get("clock", 0)
            self.logical_clock.update(received_clock)
            
            self.rank = response.get("data", {}).get("rank")
            print(f"✅ Servidor {self.server_name} registrado com rank {self.rank}")
            
        except Exception as e:
            print(f"❌ Erro ao registrar no reference server: {e}")
    
    def send_heartbeat(self):
        """✅ NOVO: Enviar heartbeat para reference server"""
        try:
            heartbeat_message = self.MessageProtocol.create_heartbeat_message(
                self.server_name,
                self.logical_clock.get()
            )
            self.ref_socket.send_string(heartbeat_message)
            response_str = self.ref_socket.recv_string()
            response = self.MessageProtocol.parse_message(response_str)
            
            # Atualizar relógio lógico
            received_clock = response.get("data", {}).get("clock", 0)
            self.logical_clock.update(received_clock)
            
        except Exception as e:
            print(f"❌ Erro no heartbeat: {e}")
    
    def start_heartbeat_thread(self):
        """✅ NOVO: Thread para heartbeats periódicos"""
        def heartbeat_loop():
            while self.running:
                self.send_heartbeat()
                time.sleep(30)  # Heartbeat a cada 30 segundos
        
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()
        print("💓 Thread de heartbeat iniciada")
    
    def synchronize_with_coordinator(self):
        """✅ NOVO: Sincronizar relógio com coordenador"""
        if not self.coordinator or self.coordinator == self.server_name:
            return
        
        try:
            # Conectar ao coordenador
            coordinator_endpoint = f"tcp://{self.coordinator}:5560"
            self.coordinator_socket.connect(coordinator_endpoint)
            
            # Enviar requisição de sincronização
            clock_message = self.MessageProtocol.create_clock_message(
                self.logical_clock.get()
            )
            self.coordinator_socket.send_string(clock_message)
            
            # Receber resposta
            response_str = self.coordinator_socket.recv_string()
            response = self.MessageProtocol.parse_message(response_str)
            
            # Atualizar relógio lógico
            received_clock = response.get("data", {}).get("clock", 0)
            self.logical_clock.update(received_clock)
            
            print(f"⏰ Sincronizado com coordenador {self.coordinator}")
            
        except Exception as e:
            print(f"❌ Erro na sincronização com coordenador: {e}")
    
    def start_election(self):
        """✅ NOVO: Iniciar eleição de coordenador"""
        print(f"🗳️ Iniciando eleição - Servidor {self.server_name} (rank {self.rank})")
        
        # Lógica de eleição simplificada
        # Em produção, isso comunicaria com outros servidores
        if self.rank == 1:  # Servidor com menor rank se torna coordenador
            self.coordinator = self.server_name
            self.announce_coordinator()
            print(f"🎖️ {self.server_name} eleito como coordenador")
    
    def announce_coordinator(self):
        """✅ NOVO: Anunciar como coordenador"""
        try:
            coordinator_message = self.MessageProtocol.create_coordinator_message(
                self.server_name,
                self.logical_clock.get()
            )
            
            # Publicar no tópico de servidores
            topic = "servers".encode('utf-8')
            self.pub_socket.send_multipart([topic, coordinator_message.encode('utf-8')])
            print(f"📢 Coordenador {self.server_name} anunciado")
            
        except Exception as e:
            print(f"❌ Erro ao anunciar coordenador: {e}")
    
    def start(self):
        # ✅ NOVO: Registrar no reference server primeiro
        self.register_with_reference()
        
        # ✅ NOVO: Iniciar eleição
        self.start_election()
        
        # ✅ NOVO: Iniciar thread de heartbeats
        self.start_heartbeat_thread()
        
        # Conectar sockets existentes
        self.rep_socket.connect("tcp://broker:5556")  # Broker Req-Rep
        self.pub_socket.connect("tcp://pubsub-proxy:5557")  # Proxy Pub/Sub
        
        print("🖥️  Servidor BBS iniciado")
        print(f"   🆔 Nome: {self.server_name}")
        print(f"   🏆 Rank: {self.rank}")
        print(f"   👑 Coordenador: {self.coordinator}")
        print(f"   ⏰ Relógio lógico: {self.logical_clock.get()}")
        print("   📨 Req-Rep: broker:5556")
        print("   📢 Pub/Sub: pubsub-proxy:5557")
        
        # ✅ NOVO: Sincronização periódica
        sync_counter = 0
        
        while True:
            try:
                # Processar requisições Req-Rep
                message_str = self.rep_socket.recv_string()
                print(f"📨 Mensagem recebida: {message_str}")
                
                # ✅ NOVO: Incrementar relógio lógico ao receber mensagem
                self.logical_clock.increment()
                
                response = self._process_message(message_str)
                
                self.rep_socket.send_string(response)
                print(f"📤 Resposta enviada: {response}")
                
                # ✅ NOVO: Sincronizar a cada 10 mensagens
                sync_counter += 1
                if sync_counter >= 10:
                    self.synchronize_with_coordinator()
                    sync_counter = 0
                
            except Exception as e:
                error_response = self._create_error_response(f"Erro interno: {str(e)}")
                self.rep_socket.send_string(error_response)
    
    def _process_message(self, message_str: str) -> str:
        try:
            message = self.MessageProtocol.parse_message(message_str)
            service = message.get("service")
            data = message.get("data", {})
            
            # ✅ NOVO: Atualizar relógio lógico com clock recebido
            received_clock = data.get("clock", 0)
            if received_clock > 0:
                self.logical_clock.update(received_clock)
            
            if service == "login":
                return self._handle_login(data)
            elif service == "users":
                return self._handle_users_list()
            elif service == "channel":
                return self._handle_channel_creation(data)
            elif service == "channels":
                return self._handle_channels_list()
            elif service == "stats":
                return self._handle_system_stats()
            elif service == "publish":
                return self._handle_publish(data)
            elif service == "message":
                return self._handle_private_message(data)
            elif service == "history":
                return self._handle_message_history(data)
            else:
                return self._create_error_response(f"Serviço desconhecido: {service}")
                
        except Exception as e:
            return self._create_error_response(f"Erro ao processar mensagem: {str(e)}")
    
    def _handle_login(self, data: dict) -> str:
        username = data.get("user", "").strip()
        
        if not username:
            return self.MessageProtocol.create_login_response(
                False, "Nome de usuário não pode estar vazio", self.logical_clock.get()
            )
        
        success = self.persistence.add_user(username)
        
        if success:
            self.persistence.record_login(username)
            self.active_users.add(username)
            return self.MessageProtocol.create_login_response(
                True, "Login realizado com sucesso", self.logical_clock.get()
            )
        else:
            return self.MessageProtocol.create_login_response(
                False, "Usuário já existe no sistema", self.logical_clock.get()
            )
    
    # ✅ NOVO: Atualizar TODOS os métodos de resposta para incluir clock
    def _handle_users_list(self) -> str:
        users = self.persistence.get_all_users()
        return self.MessageProtocol.create_users_list_response(users, self.logical_clock.get())
    
    def _handle_channel_creation(self, data: dict) -> str:
        channel_name = data.get("channel", "").strip()
        
        if not channel_name:
            return self.MessageProtocol.create_channel_response(
                False, "Nome do canal não pode estar vazio", self.logical_clock.get()
            )
        
        success = self.persistence.add_channel(channel_name)
        
        if success:
            return self.MessageProtocol.create_channel_response(
                True, f"Canal '{channel_name}' criado com sucesso", self.logical_clock.get()
            )
        else:
            return self.MessageProtocol.create_channel_response(
                False, f"Canal '{channel_name}' já existe", self.logical_clock.get()
            )
    
    def _handle_channels_list(self) -> str:
        channels = self.persistence.get_all_channels()
        return self.MessageProtocol.create_channels_list_response(channels, self.logical_clock.get())
    
    def _handle_system_stats(self) -> str:
        stats = self.persistence.get_system_stats()
        return self.MessageProtocol.create_message("stats", stats, self.logical_clock.get())
    
    def _handle_publish(self, data: dict) -> str:
        user = data.get("user", "").strip()
        channel = data.get("channel", "").strip()
        message_content = data.get("message", "").strip()
        
        if not user or not channel or not message_content:
            return self.MessageProtocol.create_publish_response(
                False, "Usuário, canal e mensagem são obrigatórios", self.logical_clock.get()
            )
        
        channels = self.persistence.get_all_channels()
        if channel not in channels:
            return self.MessageProtocol.create_publish_response(
                False, f"Canal '{channel}' não existe", self.logical_clock.get()
            )
        
        users = self.persistence.get_all_users()
        if user not in users:
            return self.MessageProtocol.create_publish_response(
                False, f"Usuário '{user}' não existe", self.logical_clock.get()
            )
        
        # ✅ NOVO: Incluir timestamp e clock na mensagem
        pub_message = self.MessageProtocol.create_pubsub_message(
            sender=user,
            content=message_content,
            target=channel,
            timestamp=datetime.now().isoformat(),
            clock=self.logical_clock.get()
        )
        
        topic = f"channel.{channel}".encode('utf-8')
        self.pub_socket.send_multipart([topic, pub_message.encode('utf-8')])
        
        message_data = {
            "type": "channel",
            "from": user,
            "to": channel,
            "content": message_content,
            "timestamp": datetime.now().isoformat(),
            "clock": self.logical_clock.get()
        }
        self.persistence.save_message(message_data)
        
        print(f"📢 Mensagem publicada no canal '{channel}': {user} -> {message_content}")
        return self.MessageProtocol.create_publish_response(
            True, "Mensagem publicada com sucesso", self.logical_clock.get()
        )
    
    def _handle_private_message(self, data: dict) -> str:
        src_user = data.get("src", "").strip()
        dst_user = data.get("dst", "").strip()
        message_content = data.get("message", "").strip()
        
        if not src_user or not dst_user or not message_content:
            return self.MessageProtocol.create_private_message_response(
                False, "Remetente, destinatário e mensagem são obrigatórios", self.logical_clock.get()
            )
        
        users = self.persistence.get_all_users()
        if dst_user not in users:
            return self.MessageProtocol.create_private_message_response(
                False, f"Usuário '{dst_user}' não existe", self.logical_clock.get()
            )
        
        if src_user not in users:
            return self.MessageProtocol.create_private_message_response(
                False, f"Usuário '{src_user}' não existe", self.logical_clock.get()
            )
        
        # ✅ NOVO: Incluir timestamp e clock na mensagem
        pub_message = self.MessageProtocol.create_pubsub_message(
            sender=src_user,
            content=message_content,
            target=dst_user,
            timestamp=datetime.now().isoformat(),
            clock=self.logical_clock.get()
        )
        
        topic = f"user.{dst_user}".encode('utf-8')
        self.pub_socket.send_multipart([topic, pub_message.encode('utf-8')])
        
        message_data = {
            "type": "private",
            "from": src_user,
            "to": dst_user,
            "content": message_content,
            "timestamp": datetime.now().isoformat(),
            "clock": self.logical_clock.get()
        }
        self.persistence.save_message(message_data)
        
        print(f"📩 Mensagem privada: {src_user} -> {dst_user}: {message_content}")
        return self.MessageProtocol.create_private_message_response(
            True, "Mensagem enviada com sucesso", self.logical_clock.get()
        )
    
    def _handle_message_history(self, data: dict) -> str:
        history_type = data.get("type", "all")
        target = data.get("target", "")
        limit = data.get("limit", 50)
        
        try:
            if history_type == "user" and target:
                messages = self.persistence.get_user_messages(target, limit)
            elif history_type == "channel" and target:
                messages = self.persistence.get_channel_messages(target, limit)
            else:
                messages = self.persistence.get_message_history(limit)
            
            return self.MessageProtocol.create_message("history", {
                "messages": messages,
                "count": len(messages),
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock.get()
            }, self.logical_clock.get())
            
        except Exception as e:
            return self.MessageProtocol.create_message("history", {
                "error": str(e),
                "messages": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
                "clock": self.logical_clock.get()
            }, self.logical_clock.get())
    
    def _create_error_response(self, description: str) -> str:
        return self.MessageProtocol.create_login_response(
            False, description, self.logical_clock.get()
        )

if __name__ == "__main__":
    # ✅ NOVO: Obter nome do servidor da variável de ambiente
    server_name = os.getenv('SERVER_NAME', 'servidor-1')
    server = BBSServer(server_name)
    server.start()