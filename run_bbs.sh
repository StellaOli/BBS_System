#!/bin/bash

# Script de execução do Sistema BBS
# Facilita iniciar, parar e gerenciar o sistema

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funções
show_menu() {
    echo ""
    echo "=========================================="
    echo "🚀 Sistema BBS - Menu Principal"
    echo "=========================================="
    echo "1. Iniciar sistema (docker-compose up)"
    echo "2. Parar sistema (docker-compose down)"
    echo "3. Ver status (docker-compose ps)"
    echo "4. Ver logs (docker-compose logs -f)"
    echo "5. Acessar cliente Python"
    echo "6. Executar testes"
    echo "7. Limpar volumes (docker-compose down -v)"
    echo "8. Reconstruir imagens (docker-compose build)"
    echo "0. Sair"
    echo "=========================================="
}

start_system() {
    echo -e "${GREEN}🚀 Iniciando Sistema BBS...${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    docker-compose up -d
    echo ""
    echo -e "${GREEN}✅ Sistema iniciado!${NC}"
    echo "Aguardando inicialização..."
    sleep 5
    
    echo ""
    echo "📊 Status dos serviços:"
    docker-compose ps
    
    echo ""
    echo "📡 Endereços:"
    echo "   Broker: localhost:5555"
    echo "   Pub/Sub: localhost:5557"
    echo "   Reference: localhost:5559"
}

stop_system() {
    echo -e "${YELLOW}🛑 Parando Sistema BBS...${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    docker-compose stop
    echo -e "${GREEN}✅ Sistema parado!${NC}"
}

show_status() {
    echo ""
    echo -e "${GREEN}📊 Status dos Serviços:${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    docker-compose ps
}

show_logs() {
    echo ""
    echo -e "${GREEN}📋 Logs do Sistema (Ctrl+C para sair):${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    docker-compose logs -f
}

access_client() {
    echo ""
    echo -e "${GREEN}🖥️  Acessando Cliente Python...${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    
    # Verificar se cliente está rodando
    if ! docker-compose ps cliente-python | grep -q "running"; then
        echo -e "${YELLOW}⚠️  Cliente não está rodando. Iniciando...${NC}"
        docker-compose up -d cliente-python
        sleep 2
    fi
    
    docker-compose exec cliente-python python client.py
}

run_tests() {
    echo ""
    echo -e "${GREEN}🧪 Executando Testes...${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    python3 run_tests.py
}

clean_volumes() {
    echo ""
    echo -e "${RED}🗑️  Limpando volumes... (isto apagará os dados)${NC}"
    read -p "Tem certeza? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        cd "$SCRIPT_DIR/Request-Reply"
        docker-compose down -v
        echo -e "${GREEN}✅ Volumes limpados!${NC}"
    else
        echo "Operação cancelada."
    fi
}

rebuild_images() {
    echo ""
    echo -e "${YELLOW}🔨 Reconstruindo imagens...${NC}"
    cd "$SCRIPT_DIR/Request-Reply"
    docker-compose build --no-cache
    echo -e "${GREEN}✅ Imagens reconstruídas!${NC}"
}

# Loop principal
while true; do
    show_menu
    read -p "Escolha uma opção: " choice
    
    case $choice in
        1) start_system ;;
        2) stop_system ;;
        3) show_status ;;
        4) show_logs ;;
        5) access_client ;;
        6) run_tests ;;
        7) clean_volumes ;;
        8) rebuild_images ;;
        0) 
            echo "Saindo..."
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opção inválida!${NC}"
            ;;
    esac
    
    read -p "Pressione Enter para continuar..."
done
