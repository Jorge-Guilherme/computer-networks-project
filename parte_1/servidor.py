import os
import datetime
from common import Socket
from os.path import join as pathjoin

SERVER_DIR = "files_server"

# Criar diretório do servidor, se não existir
if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)

server = Socket(port=5000, server=True)  # Servidor escutando na porta 5000
clientes = {}  # Dicionário para armazenar clientes conectados (endereço -> nome)

print("🚀 Servidor de chat iniciado...")

header, address = None, []

while True:
    if header is None:
        header, address = server.receiveHeaderUDP()
    else:
        if header[Socket.Header.EXTRA] == "sdw":
            break  # Comando para desligar o servidor

        # Receber arquivo e processar mensagem
        filename = server.receiveFileUDP(header, path=SERVER_DIR, append="s_")
        file_path = pathjoin(SERVER_DIR, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
        
        # 🔹 Se for um novo cliente entrando no chat
        if conteudo.startswith("hi, meu nome eh"):
            nome_usuario = conteudo.replace("hi, meu nome eh ", "").strip()
            clientes[address] = nome_usuario
            mensagem_formatada = f"{address[0]}:{address[1]}/~{nome_usuario} entrou na sala. {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"
            print(mensagem_formatada)

            # Criar arquivo com mensagem de entrada do usuário
            mensagem_path = pathjoin(SERVER_DIR, "entrada_usuario.txt")
            with open(mensagem_path, "w", encoding="utf-8") as f:
                f.write(mensagem_formatada)

            # Enviar aviso de entrada para TODOS os clientes, incluindo os antigos
            for cliente_addr in list(clientes.keys()):
                if cliente_addr != address:  # Não enviar para o próprio cliente que acabou de entrar
                    with open(mensagem_path, "rb") as f:
                        server.sendUDP(cliente_addr[1], ip=cliente_addr[0], msg=f.read(), filename="entrada_usuario.txt")
            
            # 🔹 Criar e enviar a lista de usuários para o novo cliente
            lista_usuarios = "\n".join([f"{ip}:{porta}/~{nome}" for (ip, porta), nome in clientes.items()])
            lista_path = pathjoin(SERVER_DIR, "lista_usuarios.txt")
            with open(lista_path, "w", encoding="utf-8") as f:
                f.write(f"Usuários na sala:\n{lista_usuarios}")

            with open(lista_path, "rb") as f:
                server.sendUDP(address[1], ip=address[0], msg=f.read(), filename="lista_usuarios.txt")

        # 🔹 Se um cliente sair
        elif conteudo.startswith("bye"):
            nome_usuario = clientes.get(address, "Desconhecido")

            # Criar a mensagem de saída ANTES de remover o cliente da lista
            mensagem_saida = f"{nome_usuario} saiu da sala. {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"
            saida_path = pathjoin(SERVER_DIR, "saida_usuario.txt")

            with open(saida_path, "w", encoding="utf-8") as f:
                f.write(mensagem_saida)

            print(mensagem_saida)  # Mostrar no terminal do servidor

            # 🔹 Enviar mensagem de saída para TODOS os clientes restantes ANTES de remover o cliente
            for cliente_addr in list(clientes.keys()):  
                if cliente_addr != address:  # Não enviar para o próprio cliente que saiu
                    with open(saida_path, "rb") as f:
                        server.sendUDP(cliente_addr[1], ip=cliente_addr[0], msg=f.read(), filename="saida_usuario.txt")

            # Remover cliente da lista depois de enviar a mensagem
            if address in clientes:
                del clientes[address]

        # 🔹 Se for uma mensagem comum
        else:
            nome_usuario = clientes.get(address, "Desconhecido")
            mensagem_formatada = f"{address[0]}:{address[1]}/~{nome_usuario}: {conteudo} {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}"
            print(mensagem_formatada)

            mensagem_path = pathjoin(SERVER_DIR, "mensagem_temp.txt")
            with open(mensagem_path, "w", encoding="utf-8") as f:
                f.write(mensagem_formatada)

            for cliente_addr in list(clientes.keys()):
                with open(mensagem_path, "rb") as f:
                    server.sendUDP(cliente_addr[1], ip=cliente_addr[0], msg=f.read(), filename="mensagem_temp.txt")

        header = None  # Resetar header para próxima mensagem

server.sock.close()
