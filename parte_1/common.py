# common.py - Funções comuns para comunicação UDP

import socket
from enum import IntEnum
from os.path import join as pathjoin, basename

"""
Módulo comum para gerenciamento de sockets UDP e transferência de arquivos/mensagens.
"""

class Socket: 
    HEADER_START = "HELLO"

    # Define as posições de cada um dos elementos do header de uma transferência
    class Header(IntEnum):
        START = 0
        FILENAME = 1
        DATA_LENGTH = 2
        EXTRA = 3

    def __init__(self, sock=None, ip="localhost", port=5000, buffer_size=1024, server=False):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock
        self.ip = (ip, port)
        self.buffer_size = buffer_size

        if server:
            self.sock.bind(self.ip)
            
    def sendUDP(self, port, ip="localhost", msg=[], filename="", extra=""):
        MSGLEN = len(msg)
        total_sent = 0
        destination = (ip, port)

        # Definir header da mensagem
        header = [self.HEADER_START, filename, str(MSGLEN), extra]
        self.sock.sendto(",".join(header).encode(), destination)
        
        # Enviar mensagem parcelada
        while total_sent < MSGLEN:
            total_sent += self.sock.sendto(msg[total_sent:total_sent + self.buffer_size], destination)
        
      #  if total_sent == MSGLEN:
      #      print(f"Arquivo/mensagem enviado com sucesso: {filename if filename else '[mensagem]'}")

    def receiveUDP(self):
        return self.sock.recvfrom(self.buffer_size)
    
    def receiveHeaderUDP(self):
        msg, address = self.receiveUDP()
        if msg.decode()[:len(self.HEADER_START)] == self.HEADER_START:
            header = msg.decode().split(",")
            return (header, address)
        return (None, address)
        
    def receiveFileUDP(self, header, path="output", append=""):
        self.sock.settimeout(5)
        filename = pathjoin(path, append + header[Socket.Header.FILENAME])
        
        try:
            with open(filename, "wb") as new_file:
                msg_size = 0
                while True:
                    msg, _ = self.receiveUDP()
                    msg_size += len(msg)
                    new_file.write(msg)
                    if msg_size == int(header[Socket.Header.DATA_LENGTH]):
                        break
            #    print(f"Arquivo/mensagem recebido e salvo: {filename}")
        except TimeoutError:
            print("Erro no recebimento do arquivo/mensagem")
        self.sock.settimeout(None)
        return basename(filename)

