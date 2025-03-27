import threading
import os
from common import Socket
from os.path import basename

CLIENT_DIR = "files_client"
running = True  # Controle para parar a thread de recebimento

# Criar diretório do cliente, se não existir
if not os.path.exists(CLIENT_DIR):
    os.makedirs(CLIENT_DIR)

client = Socket(port=0, server=True)  # Deixa o SO escolher uma porta livre

print("Bem-vindo ao chat baseado em arquivos 3000")

comandos = [
    "Comandos disponíveis:",
    "- hi, meu nome eh <nome> : conectar ao chat",
    "- bye                   : sair do chat",
    "- mensagem <texto>      : enviar mensagem",
    "- arquivo <nome_arquivo>: enviar arquivo",
]

for comando in comandos:
    print(comando)

nome_usuario = ""

# 🔹 Thread para escutar mensagens do servidor
def receive_messages():
    global running
    while running:
        try:
            header, _ = client.receiveHeaderUDP()
            if header:
                client.receiveFileUDP(header, path=CLIENT_DIR)
                mensagem_path = os.path.join(CLIENT_DIR, header[Socket.Header.FILENAME])
                with open(mensagem_path, "r", encoding="utf-8") as f:
                    mensagem = f.read().strip()
                    print(f"\n{mensagem}\n> ", end="")  # Exibe a mensagem no terminal
        except OSError:
            break  # Sai do loop se o socket for fechado
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")

# Criar e iniciar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receive_messages, daemon=True)
thread_recebimento.start()

# Loop principal para envio de mensagens
while True:
    msg = input("> ").strip()
    
    if msg.startswith("hi, meu nome eh"):
        nome_usuario = msg.replace("hi, meu nome eh ", "").strip()
        filename = os.path.join(CLIENT_DIR, "login.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(msg)
        with open(filename, "rb") as f:
            client.sendUDP(port=5000, msg=f.read(), filename="login.txt")
        continue
    
    if msg == "bye":
        print("Saindo do chat...")

        # Enviar notificação de saída para o servidor
        filename = os.path.join(CLIENT_DIR, "saida.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"bye {nome_usuario}")
        with open(filename, "rb") as f:
            client.sendUDP(port=5000, msg=f.read(), filename="saida.txt")

        running = False  # Para a thread de recebimento
        thread_recebimento.join()  # Espera a thread finalizar
        client.sock.close()  # Fecha o socket com segurança
        break
    
    elif msg.startswith("mensagem"):
        conteudo = msg.replace("mensagem ", "").strip()
        filename = os.path.join(CLIENT_DIR, "mensagem.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(conteudo)
        with open(filename, "rb") as f:
            client.sendUDP(port=5000, msg=f.read(), filename="mensagem.txt")
    
    elif msg.startswith("arquivo"):
        filename = msg.replace("arquivo ", "").strip()
        try:
            with open(filename, "rb") as f:
                client.sendUDP(port=5000, msg=f.read(), filename=basename(filename))
        except IOError:
            print("Nome de arquivo inválido!")

    else:
        print("Digite um comando válido!")
        for comando in comandos:
            print(comando)



