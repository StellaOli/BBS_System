import msgpack
import time
from typing import Dict, Any, List

class MessageProtocol:
    @staticmethod
    def create_message(service: str, data: Dict[str, Any], clock: int = 0) -> bytes:
        """✅ CORRETO: Formato COMPATÍVEL com Go"""
        message = {
            "service": service,
            "data": data,
            "timestamp": int(time.time()),  
            "clock": clock
        }
        return msgpack.packb(message)
    
    @staticmethod
    def parse_message(data: bytes) -> Dict[str, Any]:
        """✅ Desserializa mensagem"""
        return msgpack.unpackb(data)
    
    # ✅ MÉTODOS PARA REFERENCE SERVER
    @staticmethod
    def create_rank_message(server_name: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("rank", {"user": server_name}, clock)
    
    @staticmethod
    def create_heartbeat_message(server_name: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("heartbeat", {"user": server_name}, clock)
    
    @staticmethod
    def create_list_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("list", {}, clock)
    
    @staticmethod
    def create_clock_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("clock", {"time": int(time.time())}, clock)
    
    @staticmethod
    def create_election_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("election", {}, clock)
    
    @staticmethod
    def create_coordinator_message(coordinator: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("coordinator", {"coordinator": coordinator}, clock)
    
    # MÉTODOS PARA SISTEMA BBS
    @staticmethod
    def create_login_message(username: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("login", {"user": username}, clock)
    
    @staticmethod
    def create_login_response(success: bool, description: str = "", clock: int = 0) -> bytes:
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("login", {
            "status": status,
            "description": description
        }, clock)
    
    @staticmethod
    def create_users_list_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("users", {}, clock)
    
    @staticmethod
    def create_users_list_response(users: List[str], clock: int = 0) -> bytes:
        return MessageProtocol.create_message("users", {"users": users}, clock)
    
    @staticmethod
    def create_channel_message(channel_name: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("channel", {"channel": channel_name}, clock)
    
    @staticmethod
    def create_channel_response(success: bool, description: str = "", clock: int = 0) -> bytes:
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("channel", {
            "status": status,
            "description": description
        }, clock)
    
    @staticmethod
    def create_channels_list_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("channels", {}, clock)
    
    @staticmethod
    def create_channels_list_response(channels: List[str], clock: int = 0) -> bytes:
        return MessageProtocol.create_message("channels", {"channels": channels}, clock)
    
    @staticmethod
    def create_publish_message(user: str, channel: str, message: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("publish", {
            "user": user,
            "channel": channel,
            "message": message
        }, clock)
    
    @staticmethod
    def create_publish_response(success: bool, description: str = "", clock: int = 0) -> bytes:
        status = "OK" if success else "erro"
        return MessageProtocol.create_message("publish", {
            "status": status,
            "message": description
        }, clock)
    
    @staticmethod
    def create_private_message(src: str, dst: str, message: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("message", {
            "src": src,
            "dst": dst,
            "message": message
        }, clock)
    
    @staticmethod
    def create_private_message_response(success: bool, description: str = "", clock: int = 0) -> bytes:
        status = "OK" if success else "erro"
        return MessageProtocol.create_message("message", {
            "status": status,
            "message": description
        }, clock)
    
    @staticmethod
    def create_stats_message(clock: int = 0) -> bytes:
        return MessageProtocol.create_message("stats", {}, clock)
    
    @staticmethod
    def create_stats_response(stats: Dict[str, Any], clock: int = 0) -> bytes:
        return MessageProtocol.create_message("stats", stats, clock)
    
    @staticmethod
    def create_history_message(history_type: str, target: str = "", limit: int = 50, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("history", {
            "type": history_type,
            "target": target,
            "limit": limit
        }, clock)
    
    @staticmethod
    def create_history_response(messages: List[Dict], count: int, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("history", {
            "messages": messages,
            "count": count
        }, clock)
    
    @staticmethod
    def create_pubsub_message(sender: str, content: str, target: str = None, clock: int = 0) -> bytes:
        message = {
            "sender": sender,
            "content": content,
            "timestamp": int(time.time())  
        }
        if target:
            message["target"] = target
        if clock > 0:
            message["clock"] = clock
        return msgpack.packb(message)
    
    @staticmethod
    def create_error_response(description: str, clock: int = 0) -> bytes:
        return MessageProtocol.create_message("error", {"error": description}, clock)

    # ✅ MÉTODOS DE PARSE/UTILITÁRIOS (MANTIDOS)
    @staticmethod
    def unpack_message(data: bytes) -> Dict[str, Any]:
        """Desempacota mensagem MessagePack"""
        return msgpack.unpackb(data)
    
    @staticmethod
    def parse_pubsub_message(message: bytes) -> Dict[str, Any]:
        """Parse mensagem Pub/Sub"""
        return MessageProtocol.unpack_message(message)
    
    @staticmethod
    def extract_service_data(message_data: Dict[str, Any]) -> tuple:
        """Extrai dados comuns de resposta"""
        status = message_data.get("status", "")
        description = message_data.get("description", message_data.get("message", ""))
        return status, description
    
    @staticmethod
    def extract_clock_from_message(message: bytes) -> int:
        """Extrai valor do relógio lógico de uma mensagem"""
        try:
            data = msgpack.unpackb(message)
            return data.get("clock", 0)
        except:
            return 0

    # MÉTODOS UTILITÁRIOS PARA DEBUG
    @staticmethod
    def print_message_structure(message_bytes: bytes, label: str = "Mensagem"):
        """Debug: mostra estrutura da mensagem"""
        try:
            data = msgpack.unpackb(message_bytes)
            print(f"🔍 {label}:")
            print(f"   Service: {data.get('service')}")
            print(f"   Timestamp: {data.get('timestamp')} (tipo: {type(data.get('timestamp'))})")
            print(f"   Clock: {data.get('clock')} (tipo: {type(data.get('clock'))})")
            print(f"   Data: {data.get('data')}")
        except Exception as e:
            print(f"❌ Erro ao analisar {label}: {e}")

    @staticmethod
    def validate_go_compatibility(message_bytes: bytes) -> bool:
        """Valida se a mensagem é compatível com Go"""
        try:
            data = msgpack.unpackb(message_bytes)
            required_fields = ['service', 'data', 'timestamp', 'clock']
            
            for field in required_fields:
                if field not in data:
                    print(f"❌ Campo faltando: {field}")
                    return False
            
            # Verificar tipos
            if not isinstance(data['timestamp'], int):
                print(f"❌ Timestamp deve ser int, não {type(data['timestamp'])}")
                return False
            
            if not isinstance(data['clock'], int):
                print(f"❌ Clock deve ser int, não {type(data['clock'])}")
                return False
            
            print("✅ Mensagem compatível com Go")
            return True
            
        except Exception as e:
            print(f"❌ Erro na validação: {e}")
            return False