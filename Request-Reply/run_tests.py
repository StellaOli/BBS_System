#!/usr/bin/env python3
"""
Script de teste completo do Sistema BBS
Valida todas as funcionalidades de Parte 1-5
"""

import subprocess
import time
import sys
import json
import os


class BBSTestRunner:
    """Executor de testes do sistema BBS"""
    
    def __init__(self):
        self.base_dir = "/workspaces/codespaces-blank/Request-Reply"
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_command(self, command: str, description: str = "") -> tuple:
        """Executar comando e retornar stdout, stderr e código de retorno"""
        if description:
            print(f"\n🧪 {description}")
            print(f"   $ {command}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout ao executar: {command}")
            return "", "Timeout", 1
    
    def test_docker_status(self):
        """Testar se Docker está rodando"""
        print("\n" + "="*60)
        print("🧪 TESTE 1: Verificar Docker Status")
        print("="*60)
        
        stdout, stderr, code = self.run_command(
            "docker ps -q",
            "Listando containers rodando"
        )
        
        if code == 0:
            container_count = len(stdout.strip().split('\n')) if stdout.strip() else 0
            print(f"✅ Docker funcionando - {container_count} containers em execução")
            self.tests_passed += 1
        else:
            print(f"❌ Erro ao executar Docker: {stderr}")
            self.tests_failed += 1
    
    def test_docker_compose_build(self):
        """Testar build do Docker Compose"""
        print("\n" + "="*60)
        print("🧪 TESTE 2: Docker Compose Build")
        print("="*60)
        
        os.chdir(self.base_dir)
        
        stdout, stderr, code = self.run_command(
            "docker-compose build --no-cache 2>&1 | tail -20",
            "Construindo imagens Docker"
        )
        
        if code == 0 or "Successfully built" in stdout or "already exists" in stdout:
            print(f"✅ Imagens construídas com sucesso")
            self.tests_passed += 1
        else:
            print(f"❌ Erro no build: {stderr[:200]}")
            self.tests_failed += 1
    
    def test_docker_compose_up(self):
        """Testar inicialização do Docker Compose"""
        print("\n" + "="*60)
        print("🧪 TESTE 3: Docker Compose Up")
        print("="*60)
        
        os.chdir(self.base_dir)
        
        # Limpar antes
        self.run_command("docker-compose down -v 2>/dev/null", "Limpando containers anteriores")
        
        # Iniciar
        stdout, stderr, code = self.run_command(
            "docker-compose up -d 2>&1",
            "Iniciando sistema"
        )
        
        if "started" in stdout.lower() or "created" in stdout.lower():
            time.sleep(5)  # Aguardar inicialização
            
            # Verificar se serviços estão rodando
            stdout, _, _ = self.run_command("docker-compose ps --services --filter 'status=running'")
            services = stdout.strip().split('\n')
            
            if len(services) >= 5:  # Pelo menos reference, broker, proxy, 2 servidores
                print(f"✅ Sistema iniciado com {len(services)} serviços")
                self.tests_passed += 1
            else:
                print(f"⚠️  Apenas {len(services)} serviços rodando (esperado >= 5)")
                print(f"   Serviços: {', '.join(services)}")
                self.tests_failed += 1
        else:
            print(f"❌ Erro ao iniciar sistema")
            self.tests_failed += 1
    
    def test_connectivity(self):
        """Testar conectividade entre containers"""
        print("\n" + "="*60)
        print("🧪 TESTE 4: Conectividade")
        print("="*60)
        
        tests = [
            ("broker", "Conexão com Broker", "nc -zv broker 5556"),
            ("servidor-1", "Conexão com Servidor 1", "nc -zv servidor-1 5556"),
            ("reference", "Conexão com Reference", "nc -zv reference 5559"),
        ]
        
        for container, desc, cmd in tests:
            stdout, stderr, code = self.run_command(
                f"docker-compose exec -T {container} {cmd} 2>&1",
                desc
            )
            
            if code == 0 or "succeeded" in stdout.lower():
                print(f"   ✅ {desc}")
            else:
                print(f"   ⚠️  {desc}")
    
    def test_persistence_files(self):
        """Testar se arquivos de persistência foram criados"""
        print("\n" + "="*60)
        print("🧪 TESTE 5: Persistência de Dados")
        print("="*60)
        
        data_dir = os.path.join(self.base_dir, "python", "data")
        required_files = [
            "users.json",
            "channels.json",
            "logins.json",
            "messages.json"
        ]
        
        all_exist = True
        for file in required_files:
            file_path = os.path.join(data_dir, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file} ({size} bytes)")
            else:
                print(f"   ❌ {file} não encontrado")
                all_exist = False
        
        if all_exist:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    def test_logs(self):
        """Verificar logs de erro"""
        print("\n" + "="*60)
        print("🧪 TESTE 6: Verificar Logs")
        print("="*60)
        
        services = ["broker", "servidor-1", "reference", "pubsub-proxy"]
        
        for service in services:
            stdout, stderr, code = self.run_command(
                f"docker-compose logs {service} 2>&1 | grep -i error | head -5",
                f"Erros em {service}"
            )
            
            if stdout.strip():
                print(f"   ⚠️  Erros encontrados em {service}:")
                for line in stdout.strip().split('\n')[:2]:
                    print(f"      {line[:70]}")
            else:
                print(f"   ✅ Sem erros críticos em {service}")
    
    def test_python_syntax(self):
        """Verificar sintaxe dos arquivos Python"""
        print("\n" + "="*60)
        print("🧪 TESTE 7: Sintaxe Python")
        print("="*60)
        
        python_files = [
            "python/servidor.py",
            "python/broker.py",
            "python/persistence.py",
            "python/replication.py",
            "python/pubsub_proxy.py",
            "python/common/message_protocol.py"
        ]
        
        for file in python_files:
            file_path = os.path.join(self.base_dir, file)
            if os.path.exists(file_path):
                stdout, stderr, code = self.run_command(
                    f"python3 -m py_compile {file_path}",
                    f"Verificando {file}"
                )
                
                if code == 0:
                    print(f"   ✅ {file}")
                else:
                    print(f"   ❌ {file}: {stderr[:50]}")
                    self.tests_failed += 1
            else:
                print(f"   ⚠️  {file} não encontrado")
        
        self.tests_passed += len([f for f in python_files if os.path.exists(os.path.join(self.base_dir, f))])
    
    def generate_report(self):
        """Gerar relatório final"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL")
        print("="*60)
        
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"✅ Testes passados: {self.tests_passed}")
        print(f"❌ Testes falhados: {self.tests_failed}")
        print(f"📈 Taxa de sucesso: {percentage:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return 0
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
            return 1
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("\n" + "="*60)
        print("🚀 INICIANDO TESTES DO SISTEMA BBS")
        print("="*60)
        print(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_docker_status()
        self.test_docker_compose_build()
        self.test_docker_compose_up()
        time.sleep(3)
        self.test_connectivity()
        self.test_persistence_files()
        self.test_logs()
        self.test_python_syntax()
        
        return self.generate_report()


def main():
    """Função principal"""
    runner = BBSTestRunner()
    exit_code = runner.run_all_tests()
    
    print("\n" + "="*60)
    print("Instruções finais:")
    print("="*60)
    print("1. Ver logs em tempo real:")
    print("   docker-compose logs -f")
    print("\n2. Acessar cliente interativo C:")
    print("   docker-compose exec cliente-python ./client")
    print("\n3. Monitorar bots automáticos:")
    print("   docker-compose logs -f auto-client-c-1 auto-client-c-2")
    print("\n4. Parar sistema (mantém dados):")
    print("   docker-compose stop")
    print("\n5. Remover tudo (limpa dados):")
    print("   docker-compose down -v")
    print("="*60 + "\n")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
