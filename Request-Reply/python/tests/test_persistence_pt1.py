import sys
import os
import tempfile
import shutil
from datetime import datetime

sys.path.append('/app')

from python.persistence import BBSPersistence

def test_user_management():
    """Testa o gerenciamento de usuários"""
    print("🧪 TESTANDO GERENCIAMENTO DE USUÁRIOS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Teste 1: Adicionar usuário
        print("1. Adicionando usuários...")
        assert persistence.add_user("alice") == True, "Falha ao adicionar alice"
        assert persistence.add_user("bob") == True, "Falha ao adicionar bob"
        
        # Teste 2: Usuário duplicado
        print("2. Testando usuário duplicado...")
        assert persistence.add_user("alice") == False, "Deveria falhar ao adicionar usuário duplicado"
        
        # Teste 3: Listar usuários
        print("3. Listando usuários...")
        users = persistence.get_all_users()
        assert "alice" in users, "Alice não encontrada na lista"
        assert "bob" in users, "Bob não encontrado na lista"
        assert len(users) == 2, f"Esperado 2 usuários, encontrado {len(users)}"
        
        # Teste 4: Informações do usuário
        print("4. Obtendo informações do usuário...")
        user_info = persistence.get_user_info("alice")
        assert user_info is not None, "Informações de Alice não encontradas"
        assert user_info["username"] == "alice", "Nome de usuário incorreto"
        assert "created_at" in user_info, "Timestamp de criação faltando"
        
        print("✅ Gerenciamento de usuários: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_channel_management():
    """Testa o gerenciamento de canais"""
    print("\n🧪 TESTANDO GERENCIAMENTO DE CANAIS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Teste 1: Criar canais
        print("1. Criando canais...")
        assert persistence.add_channel("general") == True, "Falha ao criar canal general"
        assert persistence.add_channel("tech") == True, "Falha ao criar canal tech"
        assert persistence.add_channel("random") == True, "Falha ao criar canal random"
        
        # Teste 2: Canal duplicado
        print("2. Testando canal duplicado...")
        assert persistence.add_channel("general") == False, "Deveria falhar ao criar canal duplicado"
        
        # Teste 3: Listar canais
        print("3. Listando canais...")
        channels = persistence.get_all_channels()
        assert "general" in channels, "Canal general não encontrado"
        assert "tech" in channels, "Canal tech não encontrado"
        assert "random" in channels, "Canal random não encontrado"
        assert len(channels) == 3, f"Esperado 3 canais, encontrado {len(channels)}"
        
        # Teste 4: Informações do canal
        print("4. Obtendo informações do canal...")
        channel_info = persistence.get_channel_info("tech")
        assert channel_info is not None, "Informações do canal tech não encontradas"
        assert channel_info["name"] == "tech", "Nome do canal incorreto"
        assert "created_at" in channel_info, "Timestamp de criação faltando"
        
        print("✅ Gerenciamento de canais: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_login_history():
    """Testa o histórico de logins"""
    print("\n🧪 TESTANDO HISTÓRICO DE LOGINS")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Adicionar usuários primeiro
        persistence.add_user("user1")
        persistence.add_user("user2")
        
        # Teste 1: Registrar logins
        print("1. Registrando logins...")
        persistence.record_login("user1")
        persistence.record_login("user2")
        persistence.record_login("user1")  # Segundo login
        
        # Teste 2: Histórico geral
        print("2. Verificando histórico geral...")
        all_logins = persistence.get_login_history()
        assert len(all_logins) == 3, f"Esperado 3 logins, encontrado {len(all_logins)}"
        
        # Teste 3: Histórico por usuário
        print("3. Verificando histórico por usuário...")
        user1_logins = persistence.get_login_history("user1")
        assert len(user1_logins) == 2, f"Esperado 2 logins para user1, encontrado {len(user1_logins)}"
        
        user2_logins = persistence.get_login_history("user2")
        assert len(user2_logins) == 1, f"Esperado 1 login para user2, encontrado {len(user2_logins)}"
        
        # Teste 4: Estrutura dos registros de login
        print("4. Verificando estrutura dos registros...")
        login_record = all_logins[0]
        assert "username" in login_record, "Username faltando no registro"
        assert "login_time" in login_record, "Login time faltando no registro"
        assert "timestamp" in login_record, "Timestamp faltando no registro"
        
        print("✅ Histórico de logins: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_system_stats():
    """Testa as estatísticas do sistema"""
    print("\n🧪 TESTANDO ESTATÍSTICAS DO SISTEMA")
    
    test_dir = tempfile.mkdtemp()
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Popular dados de teste
        persistence.add_user("stat_user1")
        persistence.add_user("stat_user2")
        persistence.add_channel("stats_channel1")
        persistence.add_channel("stats_channel2")
        persistence.record_login("stat_user1")
        persistence.record_login("stat_user2")
        persistence.record_login("stat_user1")
        
        # Teste: Estatísticas
        print("1. Obtendo estatísticas...")
        stats = persistence.get_system_stats()
        
        assert stats["total_users"] == 2, f"Esperado 2 usuários, obtido {stats['total_users']}"
        assert stats["total_channels"] == 2, f"Esperado 2 canais, obtido {stats['total_channels']}"
        assert stats["total_logins"] == 3, f"Esperado 3 logins, obtido {stats['total_logins']}"
        assert "last_update" in stats, "Last update faltando nas estatísticas"
        
        print("✅ Estatísticas do sistema: OK")
        
    finally:
        shutil.rmtree(test_dir)

def test_backup_system():
    """Testa o sistema de backup"""
    print("\n🧪 TESTANDO SISTEMA DE BACKUP")
    
    test_dir = tempfile.mkdtemp()
    backup_dir = os.path.join(test_dir, "backups")
    
    try:
        persistence = BBSPersistence(test_dir)
        
        # Adicionar alguns dados
        persistence.add_user("backup_user")
        persistence.add_channel("backup_channel")
        persistence.record_login("backup_user")
        
        # Teste: Criar backup
        print("1. Criando backup...")
        backup_path = persistence.backup_data(backup_dir)
        
        assert os.path.exists(backup_path), "Diretório de backup não criado"
        
        # Verificar se arquivos foram copiados
        backup_files = os.listdir(backup_path)
        expected_files = ["users.json", "channels.json", "logins.json"]
        
        for expected_file in expected_files:
            assert expected_file in backup_files, f"Arquivo {expected_file} não encontrado no backup"
        
        print("✅ Sistema de backup: OK")
        
    finally:
        shutil.rmtree(test_dir)

def run_part1_tests():
    """Executa todos os testes da Parte 1"""
    print("=" * 60)
    print("🧪 TESTES DA PARTE 1 - SISTEMA BÁSICO")
    print("=" * 60)
    
    test_user_management()
    test_channel_management() 
    test_login_history()
    test_system_stats()
    test_backup_system()
    
    print("\n" + "=" * 60)
    print("🎉 TODOS OS TESTES DA PARTE 1 PASSARAM!")
    print("=" * 60)

if __name__ == "__main__":
    run_part1_tests()