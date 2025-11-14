#!/usr/bin/env python3
import zmq
import sys
sys.path.append('./python')

from common.message_protocol import MessageProtocol

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.RCVTIMEO, 5000)
socket.connect('tcp://localhost:5555')

print('Testando servidor...')
msg = MessageProtocol.create_login_message('test_user', 1)

try:
    socket.send(msg)
    response = socket.recv()
    print('✅ Resposta recebida')
except Exception as e:
    print(f'❌ Erro: {e}')
    print(f'Tipo do erro: {type(e)}')
