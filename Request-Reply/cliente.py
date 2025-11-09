import zmq
import sys
import os

# Adicionar common ao path
sys.path.append('/app/common')

class BBSClient:
    def __init__(self, broker_host="broker", broker_port=5555):
        self.broker_url = f"tcp://{broker_host}:{broker_port}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.socket.connect(self.broker_url)
        self.current_user = None
    
    def send_request(self, message: str) -> dict:
        try:
            self.socket.send_string(message)
            response_str = self.socket.recv_string()
            from common.message_protocol import MessageProtocol
            return MessageProtocol.parse_message(response_str)
        except zmq.Again:
            return {"service": "error", "data": {"status": "erro", "description": "Timeout - servidor não respondeu"}}
        except Exception as e:
            return {"service": "error", "data": {"status": "erro", "description": f"Erro de comunicação: {str(e)}"}}
    
    def login(self, username: str) -> bool:
        from common.message_protocol import MessageProtocol
        message = MessageProtocol.create_login_message(username)
        response = self.send_request(message)
        
        if response.get("service") == "login":
            data = response["data"]
            if data["status"] == "sucesso":
                self.current_user = username
                print(f"✅ {data['description']}")
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
    
    def show_help(self):
        print("\n📋 Comandos disponíveis:")
        print("  login <nome>          - Fazer login com nome de usuário")
        print("  users                 - Listar todos os usuários")
        print("  channel <nome>        - Criar um novo canal")
        print("  channels              - Listar todos os canais")
        print("  help                  - Mostrar esta ajuda")
        print("  quit                  - Sair do programa")
    
    def start_interactive(self):
        print("=== 🚀 Sistema BBS com Broker ===")
        print("Digite 'help' para ver os comandos disponíveis")
        
        while True:
            try:
                if self.current_user:
                    prompt = f"\n[{self.current_user}]> "
                else:
                    prompt = "\n[desconectado]> "
                
                command = input(prompt).strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    print("👋 Até logo!")
                    break
                
                elif cmd == "help":
                    self.show_help()
                
                elif cmd == "login":
                    if len(command) > 1:
                        self.login(command[1])
                    else:
                        print("❌ Uso: login <nome_usuario>")
                
                elif cmd == "users":
                    self.list_users()
                
                elif cmd == "channel":
                    if len(command) > 1:
                        self.create_channel(command[1])
                    else:
                        print("❌ Uso: channel <nome_canal>")
                
                elif cmd == "channels":
                    self.list_channels()
                
                else:
                    print("❌ Comando desconhecido. Digite 'help' para ajuda.")
            
            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    client = BBSClient()
    client.start_interactive()