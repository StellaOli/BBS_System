#!/usr/bin/env python3
import subprocess
import sys

with open('python/servidor.py', 'r') as f:
    content = f.read()

# Adicionar debug antes do send
debug_code = '''
                print(f"🔍 DEBUG ANTES DO SEND:")
                print(f"   Tipo da resposta: {type(response)}")
                print(f"   É bytes: {isinstance(response, bytes)}")
                print(f"   É string: {isinstance(response, str)}")
                print(f"   Tamanho: {len(response) if response else 0}")
                
                # Garantir que é bytes
                if isinstance(response, str):
                    print("💥 ERRO: Resposta é string! Convertendo...")
                    response = response.encode('utf-8')
                elif not isinstance(response, bytes):
                    print("💥 ERRO: Resposta não é bytes! Convertendo...")
                    response = str(response).encode('utf-8')
'''

if 'self.rep_socket.send(response)' in content and 'DEBUG ANTES DO SEND' not in content:
    content = content.replace(
        '                self.rep_socket.send(response)',
        debug_code + '\n                self.rep_socket.send(response)'
    )
    print("✅ Debug adicionado ao servidor")

with open('python/servidor.py', 'w') as f:
    f.write(content)

print("✅ Arquivo servidor.py atualizado")
