import zmq
import sys
import os
import threading
import time

# Adicionar common ao path
sys.path.append('/app/common')

class BBSClient:
    def __init__(self, broker_host="broker", broker_port=5555, pubsub_host="pubsub-proxy", pubsub_port=5558):
        self.broker_url = f"tcp://{broker_host}:{broker_port}"
        self.pubsub_url = f"tcp://{pubsub_host}:{pubsub_port}"
        
        self.context = zmq.Context()
        
        # Socket REQ para requisições (existente)
        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.req_socket.connect(self.broker_url)
        
        # ✅ NOVO: Socket SUB para receber mensagens
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.pubsub_url)
        
        self.current_user = None
        self.subscribed_topics = set()
        
        # Thread para receber mensagens
        self.receiving = False
        self.receive_thread = None
    
    def send_request(self, message: str) -> dict:
        try:
            self.req_socket.send_string(message)
            response_str = self.req_socket.recv_string()
            from common.message_protocol import MessageProtocol
            return MessageProtocol.parse_message(response_str)
        except zmq.Again:
            return {"service": "error", "data": {"status": "erro", "description": "Timeout - servidor não respondeu"}}
        except Exception as e:
            return {"service": "error", "data": {"status": "erro", "description": f"Erro de comunicação: {str(e)}"}}
    
    def subscribe_to_topic(self, topic: str):
        """✅ NOVO: Inscreve em um tópico Pub/Sub"""
        try:
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            self.subscribed_topics.add(topic)
            print(f"✅ Inscrito no tópico: {topic}")
        except Exception as e:
            print(f"❌ Erro ao se inscrever no tópico {topic}: {e}")
    
    def unsubscribe_from_topic(self, topic: str):
        """✅ NOVO: Cancela inscrição de um tópico"""
        try:
            self.sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic)
            self.subscribed_topics.discard(topic)
            print(f"✅ Inscrição cancelada do tópico: {topic}")
        except Exception as e:
            print(f"❌ Erro ao cancelar inscrição do tópico {topic}: {e}")
    
    def start_receiving_messages(self):
        """✅ NOVO: Inicia thread para receber mensagens"""
        if self.receiving:
            return
        
        self.receiving = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        print("📡 Ouvindo mensagens...")
    
    def stop_receiving_messages(self):
        """✅ NOVO: Para de receber mensagens"""
        self.receiving = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
    
    def _receive_loop(self):
        """✅ NOVO: Loop para receber mensagens Pub/Sub"""
        while self.receiving:
            try:
                # Timeout para verificar se ainda está recebendo
                self.sub_socket.setsockopt(zmq.RCVTIMEO, 1000)
                message = self.sub_socket.recv_string()
                
                from common.message_protocol import MessageProtocol
                msg_data = MessageProtocol.parse_pubsub_message(message)
                
                sender = msg_data.get("sender", "Desconhecido")
                content = msg_data.get("content", "")
                target = msg_data.get("target", "")
                
                if target.startswith("channel."):
                    channel = target.replace("channel.", "")
                    print(f"\n📢 [#{channel}] {sender}: {content}")
                else:
                    print(f"\n📩 [PRIVADO] {sender}: {content}")
                
            except zmq.Again:
                # Timeout, continuar loop
                continue
            except Exception as e:
                if self.receiving:  # Só mostrar erro se ainda estiver recebendo
                    print(f"❌ Erro ao receber mensagem: {e}")
    
    def login(self, username: str) -> bool:
        from common.message_protocol import MessageProtocol
        message = MessageProtocol.create_login_message(username)
        response = self.send_request(message)
        
        if response.get("service") == "login":
            data = response["data"]
            if data["status"] == "sucesso":
                self.current_user = username
                print(f"✅ {data['description']}")
                
                # ✅ NOVO: Inscrever no tópico do usuário após login
                user_topic = f"user.{username}"
                self.subscribe_to_topic(user_topic)
                self.start_receiving_messages()
                
                return True
            else:
                print(f"❌ {data['description']}")
                return False
        else:
            print(f"❌ Erro inesperado: {response}")
            return False
    
    def list_users(self):
        from common.message_protocol import MessageProtocol
        message = MessageProtocol.create_users_list_message()
        response = self.send_request(message)
        
        if response.get("service") == "users":
            users = response["data"].get("users", [])
            if users:
                print("\n👥 Usuários cadastrados:")
                for user in users:
                    print(f"  - {user}")
            else:
                print("\n📭 Nenhum usuário cadastrado")
        else:
            print(f"❌ Erro: {response['data'].get('description', 'Erro desconhecido')}")
    
    def create_channel(self, channel_name: str):
        from common.message_protocol import MessageProtocol
        message = MessageProtocol.create_channel_message(channel_name)
        response = self.send_request(message)
        
        if response.get("service") == "channel":
            data = response["data"]
            if data["status"] == "sucesso":
                print(f"✅ {data['description']}")
            else:
                print(f"❌ {data['description']}")
        else:
            print(f"❌ Erro: {response['data'].get('description', 'Erro desconhecido')}")
    
    def list_channels(self):
        from common.message_protocol import MessageProtocol
        message = MessageProtocol.create_channels_list_message()
        response = self.send_request(message)
        
        if response.get("service") == "channels":
            channels = response["data"].get("channels", [])
            if channels:
                print("\n📢 Canais disponíveis:")
                for channel in channels:
                    print(f"  - {channel}")
            else:
                print("\n📭 Nenhum canal criado")
        else:
            print(f"❌ Erro: {response['data'].get('description', 'Erro desconhecido')}")
    
    def publish_message(self, channel: str, message: str):
        """✅ NOVO: Publica mensagem em um canal"""
        if not self.current_user:
            print("❌ Você precisa estar logado para publicar mensagens")
            return
        
        from common.message_protocol import MessageProtocol
        request = MessageProtocol.create_publish_message(self.current_user, channel, message)
        response = self.send_request(request)
        
        if response.get("service") == "publish":
            data = response["data"]
            if data["status"] == "OK":
                print(f"✅ {data['message']}")
            else:
                print(f"❌ {data['message']}")
        else:
            print(f"❌ Erro: {response['data'].get('description', 'Erro desconhecido')}")
    
    def send_private_message(self, destination: str, message: str):
        """✅ NOVO: Envia mensagem privada"""
        if not self.current_user:
            print("❌ Você precisa estar logado para enviar mensagens")
            return
        
        from common.message_protocol import MessageProtocol
        request = MessageProtocol.create_private_message(self.current_user, destination, message)
        response = self.send_request(request)
        
        if response.get("service") == "message":
            data = response["data"]
            if data["status"] == "OK":
                print(f"✅ {data['message']}")
            else:
                print(f"❌ {data['message']}")
        else:
            print(f"❌ Erro: {response['data'].get('description', 'Erro desconhecido')}")
    
    def subscribe_channel(self, channel: str):
        """✅ NOVO: Inscreve em um canal"""
        topic = f"channel.{channel}"
        self.subscribe_to_topic(topic)
        print(f"✅ Inscrito no canal: {channel}")
    
    def unsubscribe_channel(self, channel: str):
        """✅ NOVO: Cancela inscrição de um canal"""
        topic = f"channel.{channel}"
        self.unsubscribe_from_topic(topic)
        print(f"✅ Inscrição cancelada do canal: {channel}")
    
    def get_message_history(self, history_type: str = "all", target: str = "", limit: int = 20):
        """✅ NOVO: Recupera histórico de mensagens"""
        from common.message_protocol import MessageProtocol
        request = MessageProtocol.create_history_request(history_type, target, limit)
        response = self.send_request(request)
        
        if response.get("service") == "history":
            data = response["data"]
            messages = data.get("messages", [])
            
            if messages:
                print(f"\n📜 Histórico ({len(messages)} mensagens):")
                for msg in messages:
                    msg_type = "Canal" if msg.get("type") == "channel" else "Privada"
                    print(f"  [{msg_type}] {msg['from']} -> {msg['to']}: {msg['content']}")
            else:
                print("\n📭 Nenhuma mensagem no histórico")
        else:
            print(f"❌ Erro ao recuperar histórico: {response}")
    
    def show_help(self):
        print("\n📋 Comandos disponíveis:")
        print("  login <nome>              - Fazer login com nome de usuário")
        print("  users                     - Listar todos os usuários")
        print("  channel <nome>            - Criar um novo canal")
        print("  channels                  - Listar todos os canais")
        print("  pub <canal> <mensagem>    - Publicar mensagem em canal")
        print("  msg <user> <mensagem>     - Enviar mensagem privada")
        print("  sub <canal>               - Inscrever em canal")
        print("  unsub <canal>             - Cancelar inscrição de canal")
        print("  history                   - Histórico geral")
        print("  history user <nome>       - Histórico de usuário")
        print("  history channel <nome>    - Histórico de canal")
        print("  help                      - Mostrar esta ajuda")
        print("  quit                      - Sair do programa")
    
    def start_interactive(self):
        print("=== 🚀 Sistema BBS - Parte 2 (Pub/Sub) ===")
        print("Digite 'help' para ver os comandos disponíveis")
        
        while True:
            try:
                if self.current_user:
                    prompt = f"\n[{self.current_user}]> "
                else:
                    prompt = "\n[desconectado]> "
                
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    self.stop_receiving_messages()
                    print("👋 Até logo!")
                    break
                
                elif cmd == "help":
                    self.show_help()
                
                elif cmd == "login":
                    if len(parts) > 1:
                        self.login(parts[1])
                    else:
                        print("❌ Uso: login <nome_usuario>")
                
                elif cmd == "users":
                    self.list_users()
                
                elif cmd == "channel":
                    if len(parts) > 1:
                        self.create_channel(parts[1])
                    else:
                        print("❌ Uso: channel <nome_canal>")
                
                elif cmd == "channels":
                    self.list_channels()
                
                elif cmd == "pub":
                    if len(parts) > 2:
                        channel = parts[1]
                        message = " ".join(parts[2:])
                        self.publish_message(channel, message)
                    else:
                        print("❌ Uso: pub <canal> <mensagem>")
                
                elif cmd == "msg":
                    if len(parts) > 2:
                        user = parts[1]
                        message = " ".join(parts[2:])
                        self.send_private_message(user, message)
                    else:
                        print("❌ Uso: msg <usuario> <mensagem>")
                
                elif cmd == "sub":
                    if len(parts) > 1:
                        self.subscribe_channel(parts[1])
                    else:
                        print("❌ Uso: sub <canal>")
                
                elif cmd == "unsub":
                    if len(parts) > 1:
                        self.unsubscribe_channel(parts[1])
                    else:
                        print("❌ Uso: unsub <canal>")
                
                elif cmd == "history":
                    if len(parts) == 1:
                        self.get_message_history()
                    elif len(parts) == 3 and parts[1] == "user":
                        self.get_message_history("user", parts[2])
                    elif len(parts) == 3 and parts[1] == "channel":
                        self.get_message_history("channel", parts[2])
                    else:
                        print("❌ Uso: history [user <nome>|channel <nome>]")
                
                else:
                    print("❌ Comando desconhecido. Digite 'help' para ajuda.")
            
            except KeyboardInterrupt:
                self.stop_receiving_messages()
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    client = BBSClient()
    client.start_interactive()