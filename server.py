import socket

HOST = '127.0.0.1'  # Endereço do localhost
PORT = 12345        # Porta para estabelecer conexões

# Criar um socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f"Servidor UDP ouvindo em {HOST}:{PORT}...")

while True:
    data, addr = server_socket.recvfrom(1024)  # Recebe até 1024 bytes
    print(f"Mensagem recebida de {addr}: {data.decode()}")
    
    # resposta ao cliente
    server_socket.sendto(b"Hello, World!", addr)
