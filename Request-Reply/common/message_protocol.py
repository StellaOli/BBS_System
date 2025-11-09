import json
from datetime import datetime
from typing import Dict, Any, List

class MessageProtocol:
    @staticmethod
    def create_message(service: str, data: Dict[str, Any]) -> str:
        message = {
            "service": service,
            "data": data
        }
        return json.dumps(message)
    
    @staticmethod
    def create_login_message(username: str) -> str:
        return MessageProtocol.create_message("login", {
            "user": username,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def create_login_response(success: bool, description: str = "") -> str:
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("login", {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "description": description
        })
    
    @staticmethod
    def create_users_list_message() -> str:
        return MessageProtocol.create_message("users", {
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def create_users_list_response(users: List[str]) -> str:
        return MessageProtocol.create_message("users", {
            "timestamp": datetime.now().isoformat(),
            "users": users
        })
    
    @staticmethod
    def create_channel_message(channel_name: str) -> str:
        return MessageProtocol.create_message("channel", {
            "channel": channel_name,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def create_channel_response(success: bool, description: str = "") -> str:
        status = "sucesso" if success else "erro"
        return MessageProtocol.create_message("channel", {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "description": description
        })
    
    @staticmethod
    def create_channels_list_message() -> str:
        return MessageProtocol.create_message("channels", {
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def create_channels_list_response(channels: List[str]) -> str:
        return MessageProtocol.create_message("channels", {
            "timestamp": datetime.now().isoformat(),
            "channels": channels
        })
    
    @staticmethod
    def parse_message(message: str) -> Dict[str, Any]:
        return json.loads(message)