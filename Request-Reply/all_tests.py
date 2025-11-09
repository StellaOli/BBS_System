import sys
import os

# Adicionar path para imports
sys.path.append('/app')

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 EXECUTANDO TODOS OS TESTES DO SISTEMA BBS")
    print("=" * 70)
    
    # Executar testes da Parte 1
    try:
        from test_persistence_pt1 import run_part1_tests
        run_part1_tests()
    except Exception as e:
        print(f"❌ Erro nos testes da Parte 1: {e}")
        return False
    
    # Executar testes da Parte 2  
    try:
        from test_persistence_pt2 import run_part2_tests
        run_part2_tests()
    except Exception as e:
        print(f"❌ Erro nos testes da Parte 2: {e}")
        return False
    
    print("🎉🎉🎉 TODOS OS TESTES PASSARAM! 🎉🎉🎉")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)