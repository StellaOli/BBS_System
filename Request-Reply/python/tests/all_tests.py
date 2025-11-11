#!/usr/bin/env python3
"""
Script principal de testes para o sistema BBS distribuído
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime

def setup_test_environment():
    """Configura ambiente de teste"""
    print("🔧 Configurando ambiente de teste...")
    
    try:
        # Verificar se todos os serviços estão rodando
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose: OK")
            
            # Contar serviços rodando
            lines = result.stdout.strip().split('\n')
            running_services = sum(1 for line in lines if "Up" in line)
            print(f"   {running_services} serviços rodando")
            
            return True
        else:
            print("❌ Docker Compose: ERRO")
            return False
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def run_persistence_tests():
    """Executa testes de persistência"""
    print("\n🚀 EXECUTANDO TESTES DE PERSISTÊNCIA")
    
    try:
        from test_persistence_pt1 import run_part1_tests
        run_part1_tests()
        
        from test_persistence_pt2 import run_part2_tests  
        run_part2_tests()
        
        return True
    except Exception as e:
        print(f"❌ Erro nos testes de persistência: {e}")
        return False

def run_integration_tests():
    """Executa testes de integração"""
    print("\n🚀 EXECUTANDO TESTES DE INTEGRAÇÃO")
    
    try:
        # Usar os testes que estão no mesmo container
        from tests.test_integration import run_integration_tests as run_int_tests
        return run_int_tests()
    except Exception as e:
        print(f"❌ Erro nos testes de integração: {e}")
        return False

def run_system_tests():
    """Executa testes de sistema"""
    print("\n🚀 EXECUTANDO TESTES DE SISTEMA")
    
    try:
        from tests.test_system import run_system_tests as run_sys_tests
        return run_sys_tests()
    except Exception as e:
        print(f"❌ Erro nos testes de sistema: {e}")
        return False

def run_quick_health_check():
    """Verificação rápida de saúde do sistema"""
    print("\n🔍 VERIFICAÇÃO RÁPIDA DE SAÚDE")
    
    services_to_check = [
        "servidor-1", "servidor-2", "servidor-3",
        "broker", "pubsub-proxy", "reference"
    ]
    
    healthy_count = 0
    
    for service in services_to_check:
        try:
            result = subprocess.run(
                ["docker", "exec", service, "echo", "ok"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"✅ {service}: SAUDÁVEL")
                healthy_count += 1
            else:
                print(f"❌ {service}: PROBLEMA")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️  {service}: TIMEOUT")
        except Exception as e:
            print(f"❌ {service}: ERRO - {e}")
    
    print(f"📊 {healthy_count}/{len(services_to_check)} serviços saudáveis")
    return healthy_count >= len(services_to_check) * 0.7  # 70% devem estar OK

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Testes do Sistema BBS Distribuído')
    parser.add_argument('--type', choices=['persistence', 'integration', 'system', 'health', 'all'],
                       default='all', help='Tipo de teste a executar')
    parser.add_argument('--quick', action='store_true', help='Executar apenas verificação rápida')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧪 SISTEMA DE TESTES BBS DISTRIBUÍDO")
    print("=" * 70)
    
    start_time = datetime.now()
    
    if args.quick:
        success = run_quick_health_check()
    else:
        # Configurar ambiente
        if not setup_test_environment():
            print("❌ Ambiente não configurado corretamente")
            sys.exit(1)
        
        # Executar testes baseado no tipo
        all_passed = True
        
        if args.type in ['persistence', 'all']:
            if not run_persistence_tests():
                all_passed = False
                
        if args.type in ['integration', 'all']:
            if not run_integration_tests():
                all_passed = False
                
        if args.type in ['system', 'all']:
            if not run_system_tests():
                all_passed = False
        
        success = all_passed
    
    # Resultados finais
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    if success:
        print(f"🎉 TESTES CONCLUÍDOS COM SUCESSO! Tempo: {duration}")
    else:
        print(f"💢 ALGUNS TESTES FALHARAM! Tempo: {duration}")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()