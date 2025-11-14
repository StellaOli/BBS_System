import sys
import os
import tempfile
import shutil
from datetime import datetime

sys.path.append('/app')

from persistence import BBSPersistence

def test_logical_clock_increment():
    """Testa se o relógio lógico incrementa antes do envio"""
    print("🧪 TESTANDO INCREMENTO DO RELÓGIO LÓGICO")
    
    # Este teste depende da sua implementação do logical_clock
    # Verificar se o clock é incrementado antes do envio
    pass

def test_logical_clock_update():
    """Testa atualização do relógio ao receber mensagem"""
    print("🧪 TESTANDO ATUALIZAÇÃO DO RELÓGIO LÓGICO")
    
    # Testar se o clock é atualizado com max(clock_local, clock_recebido)
    pass

def test_clock_in_messages():
    """Testa se todas as mensagens contêm o campo clock"""
    print("🧪 TESTANDO PRESENÇA DO CLOCK NAS MENSAGENS")
    
    test_dir = tempfile.mkdtemp()
    try:
        persistence = BBSPersistence(test_dir)
        
        # Salvar mensagem de teste
        test_message = {
            "type": "channel",
            "from": "clock_test_user",
            "to": "general", 
            "content": "Teste de clock",
            "timestamp": datetime.now().isoformat(),
            "clock": 1  # Deve ter campo clock
        }
        
        persistence.save_message(test_message)
        
        # Verificar se foi salvo com clock
        messages = persistence.get_message_history()
        assert "clock" in messages[0], "Mensagem deve conter campo clock"
        print("✅ Clock presente nas mensagens: OK")
        
    finally:
        shutil.rmtree(test_dir)

def run_clock_tests():
    """Executa todos os testes de relógio lógico"""
    print("=" * 60)
    print("⏰ TESTES DE RELÓGIO LÓGICO")
    print("=" * 60)
    
    test_clock_in_messages()
    # Adicione outros testes conforme sua implementação
    
    print("\n" + "=" * 60)
    print("🎉 TESTES DE RELÓGIO CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    run_clock_tests()