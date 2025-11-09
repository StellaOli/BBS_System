import zmq
import sys
import os

# Adicionar caminhos para imports
sys.path.append('/app')

class BBSServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        
        # Importar após adicionar ao path
        from persistence import BBSPersistence
        from common.message_protocol import MessageProtocol
        
        self.persistence = BBSPersistence()
        self.MessageProtocol = MessageProtocol
        
        self.active_users = set()
    
    def start(self):
        # Conectar ao broker
        self.socket.connect("tcp://broker:5556")
        print("🖥️  Servidor BBS conectado ao broker na porta 5556")
        print("💾 Sistema de persistência inicializado")
        
        while True:
            try:
                # Receber mensagem do broker
                message_str = self.socket.recv_string()
                print(f"📨 Mensagem recebida: {message_str}")
                
                # Processar mensagem
                response = self._process_message(message_str)
                
                # Enviar resposta via broker
                self.socket.send_string(response)
                print(f"📤 Resposta enviada: {response}")
                
            except Exception as e:
                error_response = self._create_error_response(f"Erro interno: {str(e)}")
                self.socket.send_string(error_response)
    
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
    
    def _create_error_response(self, description: str) -> str:
        return self.MessageProtocol.create_login_response(False, description)

if __name__ == "__main__":
    server = BBSServer()
    server.start()