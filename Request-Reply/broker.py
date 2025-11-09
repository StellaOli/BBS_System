import zmq

def main():
    context = zmq.Context()
    
    # Socket para clientes (ROUTER)
    client_socket = context.socket(zmq.ROUTER)
    client_socket.bind("tcp://*:5555")
    
    # Socket para servidores (DEALER)  
    server_socket = context.socket(zmq.DEALER)
    server_socket.bind("tcp://*:5556")
    
    print("🚀 Broker BBS iniciado na porta 5555 (clientes) e 5556 (servidores)")
    
    try:
        # Proxy entre clientes e servidores
        zmq.proxy(client_socket, server_socket)
    except KeyboardInterrupt:
        print("\n🛑 Broker finalizado")
    finally:
        client_socket.close()
        server_socket.close()
        context.term()

if __name__ == "__main__":
    main()