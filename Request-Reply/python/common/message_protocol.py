import json
from datetime import datetime
from typing import Dict, Any, List

class MessageProtocol:
    @staticmethod
    def create_message(service: str, data: Dict[str, Any], clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona relógio lógico a todas as mensagens"""
        message = {
            "service": service,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        if clock > 0:
            message["clock"] = clock
        return json.dumps(message)
    
    @staticmethod
    def create_login_message(username: str, clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("login", {
            "user": username
        }, clock)
    
    @staticmethod
    def create_login_response(success: bool, description: str = "", clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("login", {
            "status": status,
            "description": description
        }, clock)
    
    @staticmethod
    def create_users_list_message(clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("users", {}, clock)
    
    @staticmethod
    def create_users_list_response(users: List[str], clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("users", {
            "users": users
        }, clock)
    
    @staticmethod
    def create_channel_message(channel_name: str, clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("channel", {
            "channel": channel_name
        }, clock)
    
    @staticmethod
    def create_channel_response(success: bool, description: str = "", clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("channel", {
            "status": status,
            "description": description
        }, clock)
    
    @staticmethod
    def create_channels_list_message(clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("channels", {}, clock)
    
    @staticmethod
    def create_channels_list_response(channels: List[str], clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("channels", {
            "channels": channels
        }, clock)
    
    @staticmethod
    def parse_message(message: str) -> Dict[str, Any]:
        return json.loads(message)
    
    @staticmethod
    def create_publish_message(user: str, channel: str, message: str, clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("publish", {
            "user": user,
            "channel": channel,
            "message": message
        }, clock)
    
    @staticmethod
    def create_publish_response(success: bool, description: str = "", clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        status = "OK" if success else "erro"
        return MessageProtocol.create_message("publish", {
            "status": status,
            "message": description
        }, clock)
    
    @staticmethod
    def create_private_message(src: str, dst: str, message: str, clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        return MessageProtocol.create_message("message", {
            "src": src,
            "dst": dst,
            "message": message
        }, clock)
    
    @staticmethod
    def create_private_message_response(success: bool, description: str = "", clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona clock"""
        status = "OK" if success else "erro"
        return MessageProtocol.create_message("message", {
            "status": status,
            "message": description
        }, clock)
    
    @staticmethod
    def create_pubsub_message(sender: str, content: str, target: str = None, 
                            timestamp: str = None, clock: int = 0) -> str:
        """✅ MODIFICADO: Adiciona timestamp e clock"""
        message = {
            "sender": sender,
            "content": content,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        if target:
            message["target"] = target
        if clock > 0:
            message["clock"] = clock
        return json.dumps(message)
    
    @staticmethod
    def parse_pubsub_message(message: str) -> Dict[str, Any]:
        return json.loads(message)

    # ✅ NOVO: Métodos para parte 4 - Relógios e Sincronização
    
    @staticmethod
    def create_rank_message(server_name: str, clock: int = 0) -> str:
        """✅ NOVO: Mensagem para obter rank do servidor"""
        return MessageProtocol.create_message("rank", {
            "user": server_name
        }, clock)
    
    @staticmethod
    def create_rank_response(rank: int, clock: int = 0) -> str:
        """✅ NOVO: Resposta com rank do servidor"""
        return MessageProtocol.create_message("rank", {
            "rank": rank
        }, clock)
    
    @staticmethod
    def create_heartbeat_message(server_name: str, clock: int = 0) -> str:
        """✅ NOVO: Mensagem de heartbeat"""
        return MessageProtocol.create_message("heartbeat", {
            "user": server_name
        }, clock)
    
    @staticmethod
    def create_heartbeat_response(clock: int = 0) -> str:
        """✅ NOVO: Resposta de heartbeat"""
        return MessageProtocol.create_message("heartbeat", {
            "status": "OK"
        }, clock)
    
    @staticmethod
    def create_list_message(clock: int = 0) -> str:
        """✅ NOVO: Solicitar lista de servidores"""
        return MessageProtocol.create_message("list", {}, clock)
    
    @staticmethod
    def create_list_response(server_list: List[Dict[str, Any]], clock: int = 0) -> str:
        """✅ NOVO: Resposta com lista de servidores"""
        return MessageProtocol.create_message("list", {
            "list": server_list
        }, clock)
    
    @staticmethod
    def create_clock_message(clock: int = 0) -> str:
        """✅ NOVO: Solicitar sincronização de relógio"""
        return MessageProtocol.create_message("clock", {
            "time": datetime.now().timestamp()
        }, clock)
    
    @staticmethod
    def create_clock_response(current_time: float, clock: int = 0) -> str:
        """✅ NOVO: Resposta com tempo atual"""
        return MessageProtocol.create_message("clock", {
            "time": current_time
        }, clock)
    
    @staticmethod
    def create_election_message(clock: int = 0) -> str:
        """✅ NOVO: Iniciar eleição"""
        return MessageProtocol.create_message("election", {}, clock)
    
    @staticmethod
    def create_election_response(clock: int = 0) -> str:
        """✅ NOVO: Resposta de eleição"""
        return MessageProtocol.create_message("election", {
            "election": "OK"
        }, clock)
    
    @staticmethod
    def create_coordinator_message(coordinator: str, clock: int = 0) -> str:
        """✅ NOVO: Anunciar novo coordenador"""
        return MessageProtocol.create_message("election", {
            "coordinator": coordinator
        }, clock)
    
    @staticmethod
    def extract_service_data(message_data: Dict[str, Any]) -> tuple:
        """✅ NOVO: Extrai dados comuns de resposta"""
        status = message_data.get("status", "")
        description = message_data.get("description", message_data.get("message", ""))
        return status, description
    
    @staticmethod
    def extract_clock_from_message(message_str: str) -> int:
        """✅ NOVO: Extrai valor do relógio lógico de uma mensagem"""
        try:
            message = json.loads(message_str)
            return message.get("clock", 0)
        except:
            return 0