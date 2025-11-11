import zmq
import sys
import os
import threading
from datetime import datetime

sys.path.append('/app')

class BBSServer:
    def __init__(self):
        self.context = zmq.Context()
        
        # Socket REQ-REP (existente)
        self.rep_socket = self.context.socket(zmq.REP)
        
        # ✅ NOVO: Socket PUB para publicar mensagens
        self.pub_socket = self.context.socket(zmq.PUB)
        
        from persistence import BBSPersistence
        from common.message_protocol import MessageProtocol
        
        self.persistence = BBSPersistence()
        self.MessageProtocol = MessageProtocol
        self.active_users = set()
    
    def start(self):
        # Conectar sockets
        self.rep_socket.connect("tcp://broker:5556")  # Broker Req-Rep
        self.pub_socket.connect("tcp://pubsub-proxy:5557")  # ✅ NOVO: Proxy Pub/Sub
        
        print("🖥️  Servidor BBS iniciado")
        print("   📨 Req-Rep: broker:5556")
        print("   📢 Pub/Sub: pubsub-proxy:5557")
        
        while True:
            try:
                # Processar requisições Req-Rep
                message_str = self.rep_socket.recv_string()
                print(f"📨 Mensagem recebida: {message_str}")
                
                response = self._process_message(message_str)
                
                self.rep_socket.send_string(response)
                print(f"📤 Resposta enviada: {response}")
                
            except Exception as e:
                error_response = self._create_error_response(f"Erro interno: {str(e)}")
                self.rep_socket.send_string(error_response)
    
    def _process_message(self, message_str: str) -> str:
        try:
            message = self.MessageProtocol.parse_message(message_str)
            service = message.get("service")
            data = message.get("data", {})
            
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
            elif service == "publish":  # ✅ NOVO: Publicar em canal
                return self._handle_publish(data)
            elif service == "message":  # ✅ NOVO: Mensagem privada
                return self._handle_private_message(data)
            elif service == "history":  # ✅ NOVO: Histórico de mensagens
                return self._handle_message_history(data)
            else:
                return self._create_error_response(f"Serviço desconhecido: {service}")
                
        except Exception as e:
            return self._create_error_response(f"Erro ao processar mensagem: {str(e)}")
    
    def _handle_login(self, data: dict) -> str:
        username = data.get("user", "").strip()
        
        if not username:
            return self.MessageProtocol.create_login_response(False, "Nome de usuário não pode estar vazio")
        
        success = self.persistence.add_user(username)
        
        if success:
            self.persistence.record_login(username)
            self.active_users.add(username)
            return self.MessageProtocol.create_login_response(True, "Login realizado com sucesso")
        else:
            return self.MessageProtocol.create_login_response(False, "Usuário já existe no sistema")
    
    def _handle_users_list(self) -> str:
        users = self.persistence.get_all_users()
        return self.MessageProtocol.create_users_list_response(users)
    
    def _handle_channel_creation(self, data: dict) -> str:
        channel_name = data.get("channel", "").strip()
        
        if not channel_name:
            return self.MessageProtocol.create_channel_response(False, "Nome do canal não pode estar vazio")
        
        success = self.persistence.add_channel(channel_name)
        
        if success:
            return self.MessageProtocol.create_channel_response(True, f"Canal '{channel_name}' criado com sucesso")
        else:
            return self.MessageProtocol.create_channel_response(False, f"Canal '{channel_name}' já existe")
    
    def _handle_channels_list(self) -> str:
        channels = self.persistence.get_all_channels()
        return self.MessageProtocol.create_channels_list_response(channels)
    
    def _handle_system_stats(self) -> str:
        stats = self.persistence.get_system_stats()
        return self.MessageProtocol.create_message("stats", stats)
    
    def _handle_publish(self, data: dict) -> str:
        """✅ NOVO: Publica mensagem em um canal"""
        user = data.get("user", "").strip()
        channel = data.get("channel", "").strip()
        message_content = data.get("message", "").strip()
        
        if not user or not channel or not message_content:
            return self.MessageProtocol.create_publish_response(
                False, "Usuário, canal e mensagem são obrigatórios"
            )
        
        # Verificar se canal existe
        channels = self.persistence.get_all_channels()
        if channel not in channels:
            return self.MessageProtocol.create_publish_response(
                False, f"Canal '{channel}' não existe"
            )
        
        # Verificar se usuário existe
        users = self.persistence.get_all_users()
        if user not in users:
            return self.MessageProtocol.create_publish_response(
                False, f"Usuário '{user}' não existe"
            )
        
        # Criar mensagem para publicação
        pub_message = self.MessageProtocol.create_pubsub_message(
            sender=user,
            content=message_content,
            target=channel
        )
        
        # Publicar no canal (tópico = nome do canal)
        topic = f"channel.{channel}".encode('utf-8')
        self.pub_socket.send_multipart([topic, pub_message.encode('utf-8')])
        
        # Salvar no histórico
        message_data = {
            "type": "channel",
            "from": user,
            "to": channel,
            "content": message_content,
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
        self.persistence.save_message(message_data)
        
        print(f"📢 Mensagem publicada no canal '{channel}': {user} -> {message_content}")
        return self.MessageProtocol.create_publish_response(True, "Mensagem publicada com sucesso")
    
    def _handle_private_message(self, data: dict) -> str:
        """✅ NOVO: Envia mensagem privada para usuário"""
        src_user = data.get("src", "").strip()
        dst_user = data.get("dst", "").strip()
        message_content = data.get("message", "").strip()
        
        if not src_user or not dst_user or not message_content:
            return self.MessageProtocol.create_private_message_response(
                False, "Remetente, destinatário e mensagem são obrigatórios"
            )
        
        # Verificar se destinatário existe
        users = self.persistence.get_all_users()
        if dst_user not in users:
            return self.MessageProtocol.create_private_message_response(
                False, f"Usuário '{dst_user}' não existe"
            )
        
        # Verificar se remetente existe
        if src_user not in users:
            return self.MessageProtocol.create_private_message_response(
                False, f"Usuário '{src_user}' não existe"
            )
        
        # Criar mensagem para publicação
        pub_message = self.MessageProtocol.create_pubsub_message(
            sender=src_user,
            content=message_content,
            target=dst_user
        )
        
        # Publicar para o usuário (tópico = nome do usuário)
        topic = f"user.{dst_user}".encode('utf-8')
        self.pub_socket.send_multipart([topic, pub_message.encode('utf-8')])
        
        # Salvar no histórico
        message_data = {
            "type": "private",
            "from": src_user,
            "to": dst_user,
            "content": message_content,
            "timestamp": data.get("timestamp", datetime.now().isoformat())
        }
        self.persistence.save_message(message_data)
        
        print(f"📩 Mensagem privada: {src_user} -> {dst_user}: {message_content}")
        return self.MessageProtocol.create_private_message_response(True, "Mensagem enviada com sucesso")
    
    def _handle_message_history(self, data: dict) -> str:
        """✅ NOVO: Recupera histórico de mensagens"""
        history_type = data.get("type", "all")  # all, user, channel
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
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return self.MessageProtocol.create_message("history", {
                "error": str(e),
                "messages": [],
                "count": 0,
                "timestamp": datetime.now().isoformat()
            })
    
    def _create_error_response(self, description: str) -> str:
        return self.MessageProtocol.create_login_response(False, description)

if __name__ == "__main__":
    server = BBSServer()
    server.start()