import sys
import os
import tempfile
import shutil
from datetime import datetime

sys.path.append('/app')

from persistence import BBSPersistence

def test_message_saving():
    """Testa o salvamento de mensagens"""
    print("🧪 TESTANDO SALVAMENTO DE MENSAGENS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Teste 1: Mensagem de canal
        print("1. Salvando mensagem de canal...")
        channel_msg = {
            "type": "channel",
            "from": "user1",
            "to": "general",
            "content": "Olá pessoal!",
            "timestamp": "2024-01-15T10:00:00Z"
        }
        persistence.save_message(channel_msg)
        
        # Teste 2: Mensagem privada
        print("2. Salvando mensagem privada...")
        private_msg = {
            "type": "private", 
            "src": "user2",
            "dst": "user1",
            "message": "Oi user1!",
            "timestamp": "2024-01-15T10:01:00Z"
        }
        persistence.save_message(private_msg)
        
        # Teste 3: Mensagem com campos diferentes
        print("3. Salvando mensagem com campos alternativos...")
        alt_msg = {
            "type": "channel",
            "sender": "user3", 
            "channel": "tech",
            "content": "Mensagem técnica",
            "timestamp": "2024-01-15T10:02:00Z"
        }
        persistence.save_message(alt_msg)
        
        # Verificar se todas foram salvas
        all_messages = persistence.get_message_history()
        assert len(all_messages) == 3, f"Esperado 3 mensagens, salvo {len(all_messages)}"
        
        # Verificar estrutura padronizada
        for msg in all_messages:
            assert "id" in msg, "ID faltando"
            assert "from" in msg, "Campo 'from' faltando"
            assert "to" in msg, "Campo 'to' faltando" 
            assert "content" in msg, "Campo 'content' faltando"
            assert "timestamp" in msg, "Timestamp faltando"
            assert "saved_at" in msg, "Saved_at faltando"
        
        print("✅ Salvamento de mensagens: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_user_messages_retrieval():
    """Testa a recuperação de mensagens por usuário"""
    print("\n🧪 TESTANDO RECUPERAÇÃO POR USUÁRIO")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Criar mensagens de teste
        test_messages = [
            {"type": "private", "from": "alice", "to": "bob", "content": "Oi Bob!"},
            {"type": "private", "from": "bob", "to": "alice", "content": "Oi Alice!"},
            {"type": "channel", "from": "charlie", "to": "general", "content": "Olá todos"},
            {"type": "private", "from": "alice", "to": "charlie", "content": "Oi Charlie"},
            {"type": "channel", "from": "bob", "to": "tech", "content": "Mensagem tech"},
        ]
        
        for msg in test_messages:
            msg["timestamp"] = datetime.now().isoformat()
            persistence.save_message(msg)
        
        # Teste: Mensagens de Alice
        print("1. Mensagens de/para Alice...")
        alice_messages = persistence.get_user_messages("alice")
        assert len(alice_messages) == 3, f"Esperado 3 mensagens para Alice, obtido {len(alice_messages)}"
        
        # Verificar se inclui enviadas e recebidas
        alice_sent = [msg for msg in alice_messages if msg["from"] == "alice"]
        alice_received = [msg for msg in alice_messages if msg["to"] == "alice"]
        
        assert len(alice_sent) == 2, f"Alice deveria ter enviado 2 mensagens"
        assert len(alice_received) == 1, f"Alice deveria ter recebido 1 mensagem"
        
        # Teste: Mensagens de Bob
        print("2. Mensagens de/para Bob...")
        bob_messages = persistence.get_user_messages("bob")
        assert len(bob_messages) == 3, f"Esperado 2 mensagens para Bob, obtido {len(bob_messages)}"
        
        print("✅ Recuperação por usuário: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_channel_messages_retrieval():
    """Testa a recuperação de mensagens por canal"""
    print("\n🧪 TESTANDO RECUPERAÇÃO POR CANAL")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Criar mensagens de teste
        test_messages = [
            {"type": "channel", "from": "user1", "to": "general", "content": "Msg 1"},
            {"type": "private", "from": "user2", "to": "user1", "content": "Msg 2"},
            {"type": "channel", "from": "user3", "to": "tech", "content": "Msg 3"},
            {"type": "channel", "from": "user1", "to": "general", "content": "Msg 4"},
            {"type": "channel", "from": "user4", "to": "random", "content": "Msg 5"},
        ]
        
        for msg in test_messages:
            msg["timestamp"] = datetime.now().isoformat()
            persistence.save_message(msg)
        
        # Teste: Mensagens do canal general
        print("1. Mensagens do canal general...")
        general_messages = persistence.get_channel_messages("general")
        assert len(general_messages) == 2, f"Esperado 2 mensagens em general, obtido {len(general_messages)}"
        
        for msg in general_messages:
            assert msg["to"] == "general", "Mensagem em canal errado"
            assert msg["type"] == "channel", "Tipo de mensagem incorreto"
        
        # Teste: Mensagens do canal tech
        print("2. Mensagens do canal tech...")
        tech_messages = persistence.get_channel_messages("tech")
        assert len(tech_messages) == 1, f"Esperado 1 mensagem em tech, obtido {len(tech_messages)}"
        
        # Teste: Canal vazio
        print("3. Canal sem mensagens...")
        empty_messages = persistence.get_channel_messages("nonexistent")
        assert len(empty_messages) == 0, f"Esperado 0 mensagens, obtido {len(empty_messages)}"
        
        print("✅ Recuperação por canal: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_message_limits():
    """Testa os limites de recuperação de mensagens"""
    print("\n🧪 TESTANDO LIMITES DE MENSAGENS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Adicionar muitas mensagens
        print("1. Adicionando 25 mensagens...")
        for i in range(25):
            msg = {
                "type": "channel",
                "from": f"user{i % 5}",
                "to": "spam",
                "content": f"Message {i}",
                "timestamp": datetime.now().isoformat()
            }
            persistence.save_message(msg)
        
        # Teste: Limite no histórico geral
        print("2. Testando limite no histórico geral...")
        limited_history = persistence.get_message_history(limit=10)
        assert len(limited_history) == 10, f"Esperado 10 mensagens, obtido {len(limited_history)}"
        
        # Teste: Limite por usuário
        print("3. Testando limite por usuário...")
        user_messages = persistence.get_user_messages("user1", limit=5)
        assert len(user_messages) <= 5, f"Esperado no máximo 5 mensagens, obtido {len(user_messages)}"
        
        # Teste: Limite por canal
        print("4. Testando limite por canal...")
        channel_messages = persistence.get_channel_messages("spam", limit=3)
        assert len(channel_messages) == 3, f"Esperado 3 mensagens, obtido {len(channel_messages)}"
        
        print("✅ Limites de mensagens: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_message_ordering():
    """Testa a ordenação das mensagens"""
    print("\n🧪 TESTANDO ORDENAÇÃO DE MENSAGENS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Adicionar mensagens em ordem reversa
        timestamps = ["2024-01-15T10:00:00Z", "2024-01-15T10:01:00Z", "2024-01-15T10:02:00Z"]
        
        for i, timestamp in enumerate(reversed(timestamps)):
            msg = {
                "type": "channel",
                "from": "test_user",
                "to": "ordering_test",
                "content": f"Message {i}",
                "timestamp": timestamp
            }
            persistence.save_message(msg)
        
        # Verificar se retorna em ordem correta (mais recente primeiro)
        messages = persistence.get_message_history(limit=3)
        
        # Deveria retornar na ordem: mais recente -> mais antiga
        assert messages[0]["content"] == "Message 0", "Primeira mensagem deveria ser a mais recente"
        assert messages[2]["content"] == "Message 2", "Última mensagem deveria ser a mais antiga"
        print("✅ Ordenação de mensagens: OK")
        
    finally:
        shutil.rmtree(test_dir)

def run_part2_tests():
    """Executa todos os testes da Parte 2"""
    print("=" * 60)
    print("🧪 TESTES DA PARTE 2 - SISTEMA DE MENSAGENS")
    print("=" * 60)
    
    test_message_saving()
    test_user_messages_retrieval()
    test_channel_messages_retrieval()
    test_message_limits()
    test_message_ordering()
    
    print("\n" + "=" * 60)
    print("🎉 TODOS OS TESTES DA PARTE 2 PASSARAM!")
    print("=" * 60)

if __name__ == "__main__":
    run_part2_tests()