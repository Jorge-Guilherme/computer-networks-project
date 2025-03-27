from commands import Commands
from sender import Sender
from receiver import Receiver
from common import Socket
import os
import random
import threading
from datetime import datetime
import json

# Configurações iniciais
client = Socket(port=random.randrange(10000, 40000))
sender = Sender(socket=client)
receiver = Receiver(socket=client)
server_address = ("127.0.0.1", 5000)
username = None

# Garante que a pasta files_client existe
if not os.path.exists("files_client"):
    os.makedirs("files_client")

def save_message_file(content: str, direction: str):
    """Salva mensagem em arquivo txt e retorna o nome do arquivo"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"msg_{direction}_{timestamp}.txt"
    filepath = os.path.join("files_client", filename)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filename

def send_message_as_file(msg: str):
    """Envia mensagem como arquivo txt"""
    filename = save_message_file(msg, "out")
    with open(os.path.join("files_client", filename), 'rb') as f:
        file_data = f.read()
    
    # Envia metadados (nome do arquivo) e depois o conteúdo
    metadata = {
        'username': username,
        'filename': filename,
        'is_file': True
    }
    sender.rdt_send(json.dumps(metadata).encode(), server_address)
    sender.rdt_send(file_data, server_address)

def listen():
    while True:
        header, packet, address = client.rdt_rcv()
        sender.incoming_pkt = (header, packet, address)
        receiver.incoming_pkt = (header, packet, address)

def receive():
    while True:
        packet = receiver.wait_for_packet()
        if packet:
            try:
                metadata = json.loads(packet.decode())
                sender_username = metadata.get('username', 'Desconhecido')

                if metadata.get('is_file'):
                    content_packet = receiver.wait_for_packet()
                    message_content = content_packet.decode()
                    
                    print(f"\n📩 {sender_username}: {message_content}")  # Exibe no chat
                    save_message_file(message_content, "in")  # Salva somente mensagens exibidas
                else:
                    print(f"\n📩 {sender_username}: {metadata['message']}")
                    save_message_file(metadata['message'], "in")  # Salva apenas se exibir

            except json.JSONDecodeError:
                mensagem_recebida = packet.decode()
                print(f"\n📩 Mensagem recebida: {mensagem_recebida}")
                save_message_file(mensagem_recebida, "in")  # Salva só se aparecer no chat


def main():
    global username

    print("""
    Chat (Modo Arquivo)
    ----------------------------------
    Comandos:
      hi, meu nome eh <nome>  - Entrar na sala
      /bye                     - Sair
    ----------------------------------
    """)

    threading.Thread(target=listen, daemon=True).start()
    threading.Thread(target=receive, daemon=True).start()

    while True:
        msg = input()
        
        if not username and msg.startswith(Commands.LOGIN_CMD):
            username = msg[len(Commands.LOGIN_CMD):].strip()
            sender.rdt_send(f"{username}{Commands.USER_ENTERED}".encode(), server_address)
            print(f"\nConectado como {username}! Digite sua mensagem:")
        
        elif username and msg == Commands.LOGOUT_CMD:
            sender.rdt_send(f"{username} saiu.".encode(), server_address)
            print(f"\n{username} saiu do chat.")
            os._exit(0)
        
        elif username:
            print(f"\nVocê: {msg}")  # Exibe a mensagem enviada no chat
            send_message_as_file(msg)


if __name__ == "__main__":
    main()