from __future__ import annotations
from abc import ABC, abstractmethod
import threading
from time import process_time as t
from utils import print_elapsed
import time

from common import Socket
from utils import pretty_print, printc, bcolors

DEBUG = False

class Receiver:
    SEND_PROBABILITY = 1

    def __init__(self, state=None, socket=None) -> None:
        if state is not None:
            self.set_state(state)
        else:
            self.set_state(wait_for_below())
        self._clients = {}

        if socket is None:
            self._sock = Socket(port=5000)
        else:
            self._sock = socket
        
        self._incoming_pkt = None


    def set_state(self, state: State):
        if DEBUG:
            printc(f"> Receiver: Mudando de estado para {type(state).__name__}", bcolors.HEADER)
        self._state = state
        self._state.receiver = self
        self._state.entry_action()

    def print_state(self):
        pretty_print(f"Receiver esta em: {type(self._state).__name__}")

    @property
    def sock(self):
        return self._sock
    
    @property
    def clients(self):
        return self._clients
    
    @clients.setter
    def clients(self, clients):
        self._clients = clients

    @property
    def incoming_pkt(self):
        return self._incoming_pkt
    
    @incoming_pkt.setter
    def incoming_pkt(self, incoming_pkt):
        self._incoming_pkt = incoming_pkt

    @property
    def sndpkt(self):
        return self._sndpkt
    
    @sndpkt.setter
    def sndpkt(self, sndpkt):
        self._sndpkt = sndpkt

    @property
    def rcv_address(self):
        return self._rcv_address
    
    @rcv_address.setter
    def rcv_address(self, rcv_address):
        self._rcv_address = rcv_address

    @property
    def packet(self):
        return self._packet
    
    @packet.setter
    def packet(self, packet):
        self._packet = packet

    def rdt_send(self, data):
        return self._state.rdt_send(data)

    def rdt_rcv(self):
        return self._state.rdt_rcv()

    def wait_for_packet(self):
        return self._state.wait_for_packet()
    
    def change_state(self, state: State):
        self._state.exit_action()
        self.set_state(state)
        self._state.entry_action()
    
    # Retorna o numero de sequencia para um determinado cliente
    def seq(self, client) -> int:
        if (client in self.clients):
            return self.clients[client]
        else:
            self.clients[client] = 0
            return 0

    # Retorna o próximo numero de sequencia para um determinado cliente
    def next_seq(self, client) -> int:
        return (self.seq(client) + 1) % 2

    def receive_file(self, file_path):
        packet, address = self.wait_for_packet()
        with open(file_path, 'w') as file:
            file.write(packet.decode())

class State(ABC):    
    @property
    def receiver(self) -> Receiver:
        return self._receiver

    @receiver.setter
    def receiver(self, receiver: Receiver) -> None:
        self._receiver = receiver

    @abstractmethod
    def rdt_send(self, data) -> None:
        pass

    @abstractmethod
    def rdt_rcv(self) -> bool:
        pass

    # Ação realizada pela maquina ao sair de um estado
    @abstractmethod
    def exit_action(self) -> None:
        pass

    # Ação realizada pela maquina ao entrar em um estado
    @abstractmethod
    def entry_action(self) -> None:
        pass

    @abstractmethod
    def wait_for_packet(self) -> bytes:
        pass

class wait_for_below(State):   
    def wait_for_packet(self):
        tic = t()
        while True:
            acked = self.rdt_rcv()

            if (acked):
                if DEBUG:
                    printc(f"-> Receiver: Proximo seq para {self.receiver.rcv_address}: {self.receiver.next_seq(self.receiver.rcv_address)}", bcolors.HEADER)
                self.receiver.clients[self.receiver.rcv_address] = self.receiver.next_seq(self.receiver.rcv_address)
                self.receiver.packet = self.data
                toc = t()
                # print_elapsed(tic, toc, id="Receiver (processamento de pacote)")
                return self.receiver.packet

    def entry_action(self) -> None:
        return super().entry_action()
    
    def rdt_send(self, data) -> None:
        return super().rdt_send(data)
    
    def rdt_rcv(self) -> bool:
        # receber pacote
        if DEBUG:
            print("\n-> Receiver: Esperando pacote")
        tic = t()
        while True:
            if self.receiver.incoming_pkt is not None:
                header, packet, address = self.receiver.incoming_pkt
                self.receiver.incoming_pkt = None
                break
        toc = t()
        # print_elapsed(tic, toc, id="Receiver (espera de pacote)")
        
        # Ignorar pacotes ACKs
        if header and self.receiver.sock.has_ACK(header):
            return False
            
        self.receiver.rcv_address = address
        
        tic = t()
        if header and address and self.receiver.sock.has_SEQ(header, self.receiver.seq(address)):
            if DEBUG:
                print("-> Receiver: Envio de ACK")
            # extract data
            self.data = packet
            
            sndpkt = self.receiver.sock.make_ack(self.receiver.seq(address))
            self.receiver.sndpkt = sndpkt
            self.receiver.sock.udt_send(sndpkt, address, self.receiver.SEND_PROBABILITY)
            toc = t()
            if DEBUG:
                print_elapsed(tic, toc, id="Receiver (envio de ACK)")
            return True
        elif header and address and self.receiver.sock.has_SEQ(header, self.receiver.next_seq(address)):
            sndpkt = self.receiver.sock.make_ack(self.receiver.next_seq(address))
            self.receiver.sndpkt = sndpkt
            self.receiver.sock.udt_send(sndpkt, address, self.receiver.SEND_PROBABILITY)
            toc = t()
            if DEBUG:
                print_elapsed(tic, toc, id="Receiver (envio de ACK fora de sequencia)")
            return False
        else:
            return False
    
    def exit_action(self) -> None:
        return super().exit_action()