from datetime import datetime
from commands import Commands
from receiver import Receiver
from sender import Sender
from common import Socket
import os
import threading
import json

class Server:
    def __init__(self):
        self.server = Socket(port=5000)
        self.receiver = Receiver(socket=self.server)
        self.sender = Sender(socket=self.server)
        self.g_address = None
        self.SERVER_DIR = "files_server"
        self.connected_users = {}
        
        if not os.path.exists(self.SERVER_DIR):
            os.makedirs(self.SERVER_DIR)

    def save_received_file(self, content: str, filename: str):
        """Salva arquivo recebido no servidor"""
        filepath = os.path.join(self.SERVER_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filename

    def broadcast_file(self, filename: str, content: str, sender_address):
        """Envia arquivo para todos os clientes"""
        sender_name = next((k for k,v in self.connected_users.items() if v == sender_address), "Desconhecido")

        for user, address in self.connected_users.items():
            if address != sender_address:
                metadata = {
                    'username': sender_name,  # Nome correto do remetente
                    'filename': filename,
                    'is_file': True
                }
                self.sender.rdt_send(json.dumps(metadata).encode(), address)
                self.sender.rdt_send(content.encode(), address)


    def listen(self):
        """Ouve pacotes UDP continuamente"""
        while True:
            header, packet, address = self.server.rdt_rcv()
            self.g_address = address
            self.sender.incoming_pkt = (header, packet, address)
            self.receiver.incoming_pkt = (header, packet, address)

    def receive(self):
        """Processa pacotes recebidos"""
        print("Servidor iniciado (Modo Arquivo). Aguardando conexões...")
        
        while True:
            packet = self.receiver.wait_for_packet()
            if not packet:
                continue
                
            try:
                msg = packet.decode()
                sender_name = next((k for k,v in self.connected_users.items() if v == self.g_address), None)
                
                # Tratamento de login
                if msg.endswith(Commands.USER_ENTERED):
                    username = msg[:-len(Commands.USER_ENTERED)].strip()
                    if username and username not in self.connected_users:
                        self.connected_users[username] = self.g_address
                        print(f"⚡ {username} conectou-se")
                        self.sender.rdt_send(f"Bem-vindo(a), {username}!".encode(), self.g_address)
                
                # Tratamento de logout
                elif msg.strip() == Commands.LOGOUT_CMD and sender_name:
                    del self.connected_users[sender_name]
                    print(f"⚡ {sender_name} desconectou-se")
                    self.sender.rdt_send("logout_confirm".encode(), self.g_address)
                
                # Tratamento de arquivo
                else:
                    try:
                        metadata = json.loads(msg)
                        if metadata.get('is_file'):
                            content_packet = self.receiver.wait_for_packet()
                            content = content_packet.decode()
                            filename = self.save_received_file(content, metadata['filename'])
                            
                            print(f"📁 Arquivo recebido de {metadata['username']}: {filename}")
                            self.broadcast_file(filename, content, self.g_address)

                            # Salva apenas as mensagens que aparecerem no servidor
                            self.save_received_file(content, f"server_msg_{metadata['username']}.txt")

                    except json.JSONDecodeError:
                        if sender_name:
                            print(f"📩 {sender_name}: {msg}")
                            self.save_received_file(msg, f"server_msg_{sender_name}.txt")  # Só salva se for exibida

            except Exception as e:
                print(f"Erro: {str(e)}")


    def main(self):
        """Função principal do servidor"""
        listen_thread = threading.Thread(target=self.listen)
        receive_thread = threading.Thread(target=self.receive)
        
        listen_thread.start()
        receive_thread.start()
        
        listen_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    server = Server()
    server.main()