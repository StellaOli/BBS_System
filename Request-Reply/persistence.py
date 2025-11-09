import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class BBSPersistence:
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.channels_file = os.path.join(data_dir, "channels.json")
        self.logins_file = os.path.join(data_dir, "logins.json")
        
        # Criar diretório se não existir
        os.makedirs(data_dir, exist_ok=True)
        
        # Inicializar arquivos se não existirem
        self._initialize_files()
    
    def _initialize_files(self):
        """Inicializa os arquivos JSON com estruturas vazias se não existirem"""
        default_data = {
            self.users_file: [],
            self.channels_file: [],
            self.logins_file: []
        }
        
        for file_path, default_content in default_data.items():
            if not os.path.exists(file_path):
                self._save_json(file_path, default_content)
                print(f"📁 Arquivo criado: {file_path}")
    
    def _load_json(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Carrega dados de um arquivo JSON
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Erro ao carregar {filepath}: {e}")
            return []
    
    def _save_json(self, filepath: str, data: List[Dict[str, Any]]):
        """
        Salva dados em um arquivo JSON
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar {filepath}: {e}")
    
    def add_user(self, username: str) -> bool:
        """
        Adiciona um novo usuário ao sistema
        Retorna True se bem-sucedido, False se usuário já existe
        """
        users = self._load_json(self.users_file)
        
        # Verificar se usuário já existe
        if any(user.get("username") == username for user in users):
            print(f"⚠️  Tentativa de cadastrar usuário existente: {username}")
            return False
        
        # Adicionar novo usuário
        new_user = {
            "username": username,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        users.append(new_user)
        self._save_json(self.users_file, users)
        
        print(f"✅ Usuário cadastrado: {username}")
        return True
    
    def record_login(self, username: str):
        """
        Registra um login no histórico
        """
        logins = self._load_json(self.logins_file)
        
        login_record = {
            "username": username,
            "login_time": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp()
        }
        
        logins.append(login_record)
        self._save_json(self.logins_file, logins)
        
        print(f"📝 Login registrado: {username}")
    
    def get_all_users(self) -> List[str]:
        """
        Retorna lista de todos os usuários cadastrados
        """
        users = self._load_json(self.users_file)
        usernames = [user["username"] for user in users if user.get("username")]
        
        print(f"📊 Listando {len(usernames)} usuários")
        return usernames
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações de um usuário específico
        """
        users = self._load_json(self.users_file)
        
        for user in users:
            if user.get("username") == username:
                return user
        
        return None
    
    def add_channel(self, channel_name: str) -> bool:
        """
        Adiciona um novo canal ao sistema
        Retorna True se bem-sucedido, False se canal já existe
        """
        channels = self._load_json(self.channels_file)
        
        # Verificar se canal já existe
        if any(channel.get("name") == channel_name for channel in channels):
            print(f"⚠️  Tentativa de criar canal existente: {channel_name}")
            return False
        
        # Adicionar novo canal
        new_channel = {
            "name": channel_name,
            "created_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        channels.append(new_channel)
        self._save_json(self.channels_file, channels)
        
        print(f"✅ Canal criado: {channel_name}")
        return True
    
    def get_all_channels(self) -> List[str]:
        """
        Retorna lista de todos os canais disponíveis
        """
        channels = self._load_json(self.channels_file)
        channel_names = [channel["name"] for channel in channels if channel.get("name")]
        
        print(f"📊 Listando {len(channel_names)} canais")
        return channel_names
    
    def get_channel_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações de um canal específico
        """
        channels = self._load_json(self.channels_file)
        
        for channel in channels:
            if channel.get("name") == channel_name:
                return channel
        
        return None
    
    def get_login_history(self, username: str = None) -> List[Dict[str, Any]]:
        """
        Retorna histórico de logins
        Se username for fornecido, retorna apenas logins desse usuário
        """
        logins = self._load_json(self.logins_file)
        
        if username:
            return [login for login in logins if login.get("username") == username]
        
        return logins
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema
        """
        users = self._load_json(self.users_file)
        channels = self._load_json(self.channels_file)
        logins = self._load_json(self.logins_file)
        
        return {
            "total_users": len(users),
            "total_channels": len(channels),
            "total_logins": len(logins),
            "last_update": datetime.now().isoformat()
        }
    
    def backup_data(self, backup_dir: str = "/app/backups"):
        """
        Cria backup dos dados
        """
        import shutil
        import time
        
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = int(time.time())
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        os.makedirs(backup_path, exist_ok=True)
        
        files_to_backup = [self.users_file, self.channels_file, self.logins_file]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
        
        print(f"💾 Backup criado em: {backup_path}")
        return backup_path

# Teste da persistência
if __name__ == "__main__":
    print("🧪 Testando sistema de persistência...")
    
    persistence = BBSPersistence("./test_data")
    
    # Teste de usuários
    persistence.add_user("test_user1")
    persistence.add_user("test_user2")
    persistence.add_user("test_user1")  # Deve falar
    
    persistence.record_login("test_user1")
    
    # Teste de canais
    persistence.add_channel("general")
    persistence.add_channel("tech")
    persistence.add_channel("general")  # Deve falar
    
    # Listar dados
    print("Usuários:", persistence.get_all_users())
    print("Canais:", persistence.get_all_channels())
    print("Estatísticas:", persistence.get_system_stats())
    
    print("✅ Teste de persistência concluído!")