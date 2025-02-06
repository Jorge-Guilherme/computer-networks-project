import socket

HOST = '127.0.0.1'  # Endereço do servidor
PORT = 12345        # Porta do servidor

# Criar um socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviar uma mensagem para o servidor
message = "Olá, servidor!"
client_socket.sendto(message.encode(), (HOST, PORT))

# resposta do servidor
data, _ = client_socket.recvfrom(1024)
print("Mensagem do servidor:", data.decode())

client_socket.close()
