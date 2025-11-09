import zmq

def main():
    context = zmq.Context()
    
    # Socket para subscribers (XSUB)
    sub_socket = context.socket(zmq.XSUB)
    sub_socket.bind("tcp://*:5557")
    
    # Socket para publishers (XPUB)  
    pub_socket = context.socket(zmq.XPUB)
    pub_socket.bind("tcp://*:5558")
    
    print("🔔 Proxy Pub/Sub iniciado na porta 5557 (XSUB) e 5558 (XPUB)")
    
    try:
        # Proxy entre publishers e subscribers
        zmq.proxy(sub_socket, pub_socket)
    except KeyboardInterrupt:
        print("\n🛑 Proxy Pub/Sub finalizado")
    finally:
        sub_socket.close()
        pub_socket.close()
        context.term()

if __name__ == "__main__":
    main()