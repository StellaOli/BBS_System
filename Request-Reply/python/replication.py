"""
Sistema de Replicação de Dados - Parte 5
Implementa Write-All, Read-Any com sincronização periódica
"""

import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Any


class DataReplicationManager:
    """
    Gerencia replicação de dados entre servidores
    Estratégia: Write-All, Read-Any com sincronização eventual
    """
    
    def __init__(self, server_name: str, data_dir: str = "/app/data"):
        self.server_name = server_name
        self.data_dir = data_dir
        self.replication_log_file = os.path.join(data_dir, f"replication_{server_name}.log")
        self.last_sync_file = os.path.join(data_dir, "last_sync.json")
        
        # Inicializar diretório
        os.makedirs(data_dir, exist_ok=True)
        
        # Histórico de operações para replicação
        self.operation_log: List[Dict[str, Any]] = []
        self.operation_counter = 0
        
        # Carregar log existente
        self._load_operation_log()
    
    def _load_operation_log(self):
        """Carregar histórico de operações do disco"""
        try:
            if os.path.exists(self.replication_log_file):
                with open(self.replication_log_file, 'r') as f:
                    self.operation_log = json.load(f)
                    self.operation_counter = len(self.operation_log)
                    print(f"📜 Histórico de replicação carregado: {self.operation_counter} operações")
            else:
                self.operation_log = []
                self.operation_counter = 0
        except Exception as e:
            print(f"⚠️  Erro ao carregar log de replicação: {e}")
            self.operation_log = []
    
    def _save_operation_log(self):
        """Salvar histórico de operações"""
        try:
            with open(self.replication_log_file, 'w') as f:
                json.dump(self.operation_log, f, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar log de replicação: {e}")
    
    def log_operation(self, operation: str, payload: Dict[str, Any], timestamp: float = None) -> Dict[str, Any]:
        """
        Registrar uma operação para replicação
        
        Args:
            operation: Tipo de operação (add_user, add_channel, save_message, etc)
            payload: Dados da operação
            timestamp: Timestamp da operação (opcional)
        
        Returns:
            Registro da operação com ID e metadados
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.operation_counter += 1
        
        operation_record = {
            "id": self.operation_counter,
            "server": self.server_name,
            "operation": operation,
            "payload": payload,
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat()
        }
        
        self.operation_log.append(operation_record)
        self._save_operation_log()
        
        print(f"📝 Operação registrada #{self.operation_counter}: {operation}")
        return operation_record
    
    def get_operations_since(self, operation_id: int) -> List[Dict[str, Any]]:
        """
        Obter todas as operações desde um ID específico
        Usado para sincronizar com outros servidores
        
        Args:
            operation_id: ID da última operação conhecida
        
        Returns:
            Lista de operações posteriores
        """
        return [op for op in self.operation_log if op["id"] > operation_id]
    
    def apply_remote_operation(self, operation_record: Dict[str, Any]) -> bool:
        """
        Aplicar uma operação recebida de outro servidor
        
        Args:
            operation_record: Registro de operação remota
        
        Returns:
            True se aplicado com sucesso, False caso contrário
        """
        try:
            operation = operation_record.get("operation")
            payload = operation_record.get("payload")
            op_id = operation_record.get("id")
            
            # Evitar duplicatas verificando ID
            if any(op["id"] == op_id and op["server"] == operation_record.get("server") 
                   for op in self.operation_log):
                print(f"⏭️  Operação duplicada ignorada: #{op_id}")
                return False
            
            # Aplicar operação
            print(f"📥 Aplicando operação remota #{op_id}: {operation}")
            
            # Aqui você aplicaria a operação ao estado local
            # Por exemplo: adicionar usuário, canal, mensagem, etc
            
            self.operation_log.append(operation_record)
            self._save_operation_log()
            
            print(f"✅ Operação remota aplicada: #{op_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar operação remota: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Obter status de sincronização"""
        return {
            "server": self.server_name,
            "operation_count": len(self.operation_log),
            "last_operation_id": self.operation_log[-1]["id"] if self.operation_log else 0,
            "timestamp": time.time()
        }
    
    def get_full_snapshot(self) -> Dict[str, Any]:
        """Obter snapshot completo do estado para sincronização total"""
        return {
            "server": self.server_name,
            "operations": self.operation_log,
            "timestamp": time.time()
        }
    
    def apply_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Aplicar snapshot completo de outro servidor"""
        try:
            remote_ops = snapshot.get("operations", [])
            remote_server = snapshot.get("server")
            
            print(f"📥 Aplicando snapshot de {remote_server}: {len(remote_ops)} operações")
            
            # Mesclar operações, evitando duplicatas
            for remote_op in remote_ops:
                if not any(op["id"] == remote_op["id"] and op["server"] == remote_op["server"] 
                          for op in self.operation_log):
                    self.operation_log.append(remote_op)
            
            # Ordenar por timestamp
            self.operation_log.sort(key=lambda x: x["timestamp"])
            
            self._save_operation_log()
            print(f"✅ Snapshot aplicado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar snapshot: {e}")
            return False


class ServerReplicationSynchronizer:
    """
    Sincroniza dados entre múltiplos servidores
    Implementa comunicação peer-to-peer para replicação
    """
    
    def __init__(self, replication_manager: DataReplicationManager, 
                 other_servers: List[str] = None):
        self.replication_manager = replication_manager
        self.other_servers = other_servers or []
        self.sync_interval = 60  # Sincronizar a cada 60 segundos
        self.last_sync_time = {}
    
    def start_sync_thread(self):
        """Iniciar thread de sincronização periódica"""
        def sync_loop():
            print("🔄 Thread de sincronização iniciada")
            while True:
                try:
                    time.sleep(self.sync_interval)
                    self.sync_with_peers()
                except Exception as e:
                    print(f"❌ Erro no loop de sincronização: {e}")
        
        thread = threading.Thread(target=sync_loop, daemon=True)
        thread.start()
        print("✅ Sincronização periódica ativada")
    
    def sync_with_peers(self):
        """Sincronizar com todos os peers conhecidos"""
        print(f"\n🔄 Iniciando sincronização com peers...")
        
        for peer in self.other_servers:
            try:
                if peer == self.replication_manager.server_name:
                    continue  # Não sincronizar consigo mesmo
                
                print(f"📡 Sincronizando com {peer}...")
                self._sync_with_peer(peer)
                
            except Exception as e:
                print(f"⚠️  Erro ao sincronizar com {peer}: {e}")
    
    def _sync_with_peer(self, peer: str):
        """
        Sincronizar com um peer específico
        Em uma implementação real, isto usaria ZeroMQ REQ-REP
        """
        # Nota: Esta é uma implementação simplificada
        # Em produção, isto comunicaria via socket REQ-REP
        print(f"   💫 Sincronizando dados com {peer}")
        self.last_sync_time[peer] = time.time()


class ConsistencyGuarantees:
    """
    Implementa garantias de consistência
    Write-All, Read-Any com ordenação causal
    """
    
    @staticmethod
    def validate_causal_ordering(operations: List[Dict[str, Any]]) -> bool:
        """
        Validar ordenação causal das operações
        Garantir que operações dependentes mantêm ordem
        """
        timestamps = []
        for op in operations:
            timestamps.append(op["timestamp"])
        
        # Verificar se timestamps estão em ordem (ao menos localmente)
        return all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps)-1))
    
    @staticmethod
    def detect_conflict(op1: Dict[str, Any], op2: Dict[str, Any]) -> bool:
        """
        Detectar conflito entre duas operações
        Por exemplo: dois servidores criando mesmo canal ao mesmo tempo
        """
        # Conflito se mesma operação em mesmo recurso
        if op1["operation"] == op2["operation"]:
            if op1["operation"] == "add_channel":
                return op1["payload"].get("name") == op2["payload"].get("name")
            elif op1["operation"] == "add_user":
                return op1["payload"].get("username") == op2["payload"].get("username")
        
        return False
    
    @staticmethod
    def resolve_conflict(op1: Dict[str, Any], op2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolver conflito entre operações
        Estratégia: Last-Write-Wins (ordenado por timestamp)
        """
        if op1["timestamp"] < op2["timestamp"]:
            return op2
        elif op2["timestamp"] < op1["timestamp"]:
            return op1
        else:
            # Desempate: usar nome do servidor
            if op1["server"] < op2["server"]:
                return op1
            else:
                return op2
