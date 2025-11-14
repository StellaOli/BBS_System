#!/usr/bin/env python3
import sys
import os
sys.path.append('/app')

from common.message_protocol import MessageProtocol

print("🧪 Testando serialização...")

# Testar criação de mensagem de login
login_msg = MessageProtocol.create_login_message("test_user", 1)
print(f"📤 Mensagem login: {type(login_msg)} - {len(login_msg)} bytes")

# Testar criação de resposta
login_response = MessageProtocol.create_login_response(True, "Login bem-sucedido", 2)
print(f"📥 Resposta login: {type(login_response)} - {len(login_response)} bytes")

# Testar parse da resposta
try:
    parsed = MessageProtocol.parse_message(login_response)
    print(f"✅ Parse OK: {parsed}")
except Exception as e:
    print(f"❌ Parse falhou: {e}")

# Testar estrutura específica que o cliente C espera
print("\\n🔍 Estrutura da resposta:")
print(f"  service: {parsed.get('service')}")
print(f"  data: {parsed.get('data')}")
print(f"  timestamp: {parsed.get('timestamp')} (tipo: {type(parsed.get('timestamp'))})")
print(f"  clock: {parsed.get('clock')} (tipo: {type(parsed.get('clock'))})")
