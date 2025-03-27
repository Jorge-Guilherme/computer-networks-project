import random
import socket
from os.path import join as pathjoin
from os.path import basename
from time import process_time as t
from utils import print_elapsed, bcolors, printc

'''
Funções comuns a serem usadas pelos sockets

'''
DEBUG = False


class Socket: 
    HEADER_START = "HELLO"
    PACKET_START = "HELLOPKT"

    # define as posições de cada um dos elementos do header de uma transferência
    class Header:
        START = 0
        FILENAME = 1
        DATA_LENGTH = 2
        EXTRA = 3

    class PacketHeader:
        START = 0
        ACK = 1
        SEQ = 2
        DATA = 3

    def __init__(self, sock=None, ip="localhost", port=None, buffer_size=1024):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock

        self.buffer_size = buffer_size

        if port and ip:
            self.address = (ip, port)
            self.sock.bind(self.address)

        hostname = socket.gethostname()
        host = socket.gethostbyname(hostname)
        if DEBUG:
            printc(f"Iniciando socket em {hostname}: {host} [{port}]")

    def receiveUDP(self):
        return self.sock.recvfrom(self.buffer_size)
    
    @property
    def HEADERLEN(self) -> int:
        return len(','.join([self.PACKET_START, "0", "0", "0"]))
    
    # Espera o recebimento de um pacote
    def rdt_rcv(self):
        tic = t()
        msg, address = self.receiveUDP()

        if msg[:len(self.PACKET_START)].decode() == self.PACKET_START:
            header = msg[:self.HEADERLEN - 1].decode().split(",")
            packet = msg[self.HEADERLEN - 1:]
            if DEBUG:
                print(f"-> Pacote recebido: seq={header[self.PacketHeader.SEQ]}, ack={header[self.PacketHeader.ACK]}")
                toc = t()
                print_elapsed(tic, toc, id="Socket (recebimento de pacote)")
            return (header, packet, address)
        
        return (None, None, address)
    
    # Envia pacotes via UDP. simula perdas de acordo com probability
    def udt_send(self, data, address, probability=1.0):
        rand = random.random()
        if DEBUG:
            printc (f"-> Enviando: {data[:32]}... para: {address}", bcolors.OKBLUE)
        if rand < probability:
            try:
                return self.sock.sendto(data, address)
            except:
                printc("== ! Erro na conexão ! ==", bcolors.FAIL)
                return 0
        else:
            printc("== ! Simulando falha na transmissão ! ==", bcolors.FAIL)
            return 0
    
    # Cria um pacote com os bits seq e ack, mais um header
    def make_pkt(self, seq, data, ack=0):
        tic = t()
        # 1) definir header da mensagem
        #                            ↱ "bit" 'ack' do pacote
        msg = [self.PACKET_START, str(ack), str(seq)]
        #         ↳ identificador do header  ↳ "bit" 'seq' do pacote

        msg = ",".join(msg).encode()

        # 2) calcular tamanho do header em bytes
        HEADERLEN = len(msg)

        if data and len(data) + HEADERLEN > self.buffer_size:
            raise Exception ("Pacote não pode ser maior do que buffer_size")
        
        # 3) adicionar mensagem ao pacote
        if isinstance(data, bytes):
            msg = msg + b"," + data
        else:
            msg = msg + b"," + data.encode()

        if DEBUG:
            print(f"-> Pacote criado: {msg[:HEADERLEN]}")
            toc = t()
            print_elapsed(tic, toc, id="Socket (criação de pacote)")
        # 4) criar pacote
        return msg
    
    # Retorna o proximo numero seq
    def next_seq(self, seq):
        return (seq + 1) % 2
    
    # Verifica se um pacote tem o bit ACK 
    def has_ACK(self, rcvpkt):
        pkt_ack = int(rcvpkt[self.PacketHeader.ACK])
        #print (f"# Check: is_ACK?: {pkt_ack == 1}")
        return pkt_ack == 1
    
    # Verifica se um pacote tem o bit ACK e o seq é igual ao seq especificado
    def is_ACK(self, rcvpkt, seq):
        pkt_ack = int(rcvpkt[self.PacketHeader.ACK])
        pkt_seq = int(rcvpkt[self.PacketHeader.SEQ])
        #print (f"# Check: is_ACK?: {pkt_ack == 1 and pkt_seq == seq}")
        #print (f"-> ack bit: {pkt_ack} | seq bit: {pkt_seq}, expected: {seq}")
        return pkt_ack == 1 and pkt_seq == seq
    
    # Verifica se o seq de um pacote é igual ao seq especificado
    def has_SEQ(self, rcvpkt, seq):
        pkt_seq = int(rcvpkt[self.PacketHeader.SEQ])
        #print (f"# Check: has_SEQ?: {pkt_seq == seq}")
        #print (f"-> seq bit: {pkt_seq}, expected: {seq}")
        return pkt_seq == seq
    
    def make_ack(self, seq):
        return self.make_pkt(seq=seq, data="", ack=1)
        
    # Espera o recebimento de um header
    def receive_header(self):
        msg, address = self.receiveUDP()
        print(msg.decode())

        if msg.decode()[:len(self.HEADER_START)] == self.HEADER_START:
            header = msg.decode().split(",")
            if DEBUG:
                print(f"-> Header recebido: {header}")
            return (header, address)
        
        return (None, address)
        
    # Recebe e salva um arquivo segundo as especificações de um header, usando RDT 3.0
    def receive_file(self, header, receiver, path="output", append=""):
        filename = pathjoin(path, append + header[Socket.Header.FILENAME])
        try:
            tic = t()
            with open(filename, "wb") as new_file:
                msg_size = 0
                datalen = int(header[Socket.Header.DATA_LENGTH])
                while True:
                    msg = receiver.wait_for_packet()
                    msg_size += len(msg)
                    new_file.write(msg)
                    printc (f"== Transferidos {msg_size}/{datalen} bytes ==", bcolors.WARNING)
                    # parar quando tiver recebido todos os bytes especificados no header
                    if msg_size == datalen:
                        printc("== ! Transferência completa ! ==", bcolors.OKGREEN)
                        break
                printc(f"== ! Arquivo salvo: {filename} ! ==", bcolors.OKGREEN)
            toc = t()
            print_elapsed(tic, toc, id="Socket (recebimento de arquivo)")
        except TimeoutError:
            printc ("-> Erro no recebimento do arquivo <-", bcolors.FAIL)
        # desligar o timeout
        return filename
    
    # Envia um arquivo usando RDT 3.0
    def send_file(self, port, sender, ip="localhost", msg=[], filename="", extra=""):
        tic = t()
        # 1) calcular tamanho da mensagem em bytes
        MSGLEN = len(msg)
        total_sent = 0
        destination = (ip, port)

        # 2) definir header da mensagem
        #                              ↱ nome do arquivo
        header = [Socket.HEADER_START, filename, str(MSGLEN), extra]
        #         ↳ identificador do header     |              ↳ mensagem extra
        #                                        ↳ tamanho da mensagem

        # 3) enviar header da mensagem
        if DEBUG:
            print(f"-> Enviando um header de {len(header)} bytes")
        sender.rdt_send(data=",".join(header), address=destination)

        # 4) enviar mensagem parcelada em pacotes tamanho buffer_size
        print(f"-> Enviando um arquivo de {MSGLEN} bytes")
        while total_sent <= MSGLEN: # enquanto a mensagem ainda não foi completamente enviada
            next_sent = total_sent + 1024 - self.HEADERLEN
            sender.rdt_send(data=msg[total_sent:next_sent], address=destination)
            total_sent = next_sent
            #print(f"> Bytes enviados: {total_sent}")

        if total_sent > 0 and total_sent == MSGLEN: 
            printc(f"-> Arquivo enviado com sucesso: {filename}", bcolors.OKGREEN)

        toc = t()
        print_elapsed(tic, toc, id="Socket (envio de arquivo)")
    
    
        
