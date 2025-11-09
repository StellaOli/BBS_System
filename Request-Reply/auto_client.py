import zmq
import sys
import os
import time
import random
import threading

sys.path.append('/app/common')

from common.message_protocol import MessageProtocol

class AutoBBSClient:
    def __init__(self, broker_host="broker", broker_port=5555, pubsub_host="pubsub-proxy", pubsub_port=5558):
        self.broker_url = f"tcp://{broker_host}:{broker_port}"
        self.pubsub_url = f"tcp://{pubsub_host}:{pubsub_port}"
        
        self.context = zmq.Context()
        self.req_socket = self.context.socket(zmq.REQ)
        self.req_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.req_socket.connect(self.broker_url)
        
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.pubsub_url)
        
        self.username = f"bot_{random.randint(1000, 9999)}"
        self.receiving = False
        self.receive_thread = None
        
        # Mensagens pré-definidas para os bots
        self.messages = [
            "Olá pessoal!",
            "Como vocês estão?",
            "Alguém online?",
            "Que dia lindo!",
            "Alguma novidade?",
            "Estou testando o sistema",
            "Funcionando perfeitamente!",
            "Mensagem automática de teste",
            "Hello world!",
            "Sistema BBS é incrível!"
        ]
        
        # Canais disponíveis
        self.available_channels = ["geral", "tech", "random", "offtopic", "testes"]
    
    def send_request(self, message: str) -> dict:
        try:
            self.req_socket.send_string(message)
            response_str = self.req_socket.recv_string()
            return MessageProtocol.parse_message(response_str)
        except zmq.Again:
            return {"service": "error", "data": {"status": "erro", "description": "Timeout"}}
        except Exception as e:
            return {"service": "error", "data": {"status": "erro", "description": f"Erro: {str(e)}"}}
    
    def login(self):
        """Faz login com nome aleatório"""
        message = MessageProtocol.create_login_message(self.username)
        response = self.send_request(message)
        
        if response.get("service") == "login" and response["data"]["status"] == "sucesso":
            print(f"🤖 {self.username} conectado")
            
            # Inscrever no próprio usuário e em alguns canais
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, f"user.{self.username}")
            for channel in random.sample(self.available_channels, 2):
                self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, f"channel.{channel}")
                print(f"🤖 {self.username} inscrito em: {channel}")
            
            return True
        else:
            print(f"❌ {self.username} falhou no login")
            return False
    
    def ensure_channels_exist(self):
        """Garante que os canais existam"""
        for channel in self.available_channels:
            message = MessageProtocol.create_channel_message(channel)
            response = self.send_request(message)
            if response.get("service") == "channel":
                if response["data"]["status"] == "sucesso":
                    print(f"🤖 Canal criado: {channel}")
                # Se já existe, não faz nada
    
    def start_receiving(self):
        """Inicia thread para receber mensagens"""
        self.receiving = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
    
    def stop_receiving(self):
        """Para de receber mensagens"""
        self.receiving = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
    
    def _receive_loop(self):
        """Loop para receber mensagens"""
        while self.receiving:
            try:
                self.sub_socket.setsockopt(zmq.RCVTIMEO, 1000)
                message = self.sub_socket.recv_string()
                
                msg_data = MessageProtocol.parse_pubsub_message(message)
                sender = msg_data.get("sender", "Desconhecido")
                content = msg_data.get("content", "")
                target = msg_data.get("target", "")
                
                # Ignora próprias mensagens
                if sender != self.username:
                    if target.startswith("channel."):
                        channel = target.replace("channel.", "")
                        print(f"🤖 {self.username} recebeu em #{channel}: {sender}: {content}")
                    else:
                        print(f"🤖 {self.username} recebeu privado: {sender}: {content}")
                        
            except zmq.Again:
                continue
            except Exception as e:
                if self.receiving:
                    print(f"🤖 Erro ao receber: {e}")
    
    def send_random_message(self):
        """Envia uma mensagem aleatória"""
        channel = random.choice(self.available_channels)
        message = random.choice(self.messages)
        
        request = MessageProtocol.create_publish_message(self.username, channel, message)
        response = self.send_request(request)
        
        if response.get("service") == "publish" and response["data"]["status"] == "OK":
            print(f"🤖 {self.username} publicou em #{channel}: {message}")
        else:
            print(f"🤖 {self.username} falhou ao publicar")
    
    def run(self):
        """Loop principal do cliente automático"""
        print(f"🚀 Iniciando cliente automático: {self.username}")
        
        # Login e setup
        if not self.login():
            return
        
        self.ensure_channels_exist()
        self.start_receiving()
        
        try:
            message_count = 0
            while message_count < 10:  # Envia 10 mensagens
                # Espera entre 2 e 5 segundos
                wait_time = random.uniform(2.0, 5.0)
                time.sleep(wait_time)
                
                self.send_random_message()
                message_count += 1
            
            print(f"✅ {self.username} completou 10 mensagens. Continuando a ouvir...")
            
            # Continua ouvindo mensagens indefinidamente
            while True:
                time.sleep(10)
                
        except KeyboardInterrupt:
            print(f"\n🛑 {self.username} interrompido")
        finally:
            self.stop_receiving()
            print(f"👋 {self.username} finalizado")

if __name__ == "__main__":
    client = AutoBBSClient()
    client.run()