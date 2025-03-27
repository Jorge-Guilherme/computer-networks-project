# Primeira etapa: Envio de arquivos via UDP

## Inicializando o código

Inicialize o cliente

    python ./cliente.py

Em outra janela, inicialize o servidor

    python ./servidor.py

## Comandos

| Funcionalidade                        |  Comando                             |
|---------------------------------------|--------------------------------------|
| Conectar à sala                       |  hi, meu nome eh <nome_do_usuario>   |
| Sair da sala                          |  /bye                                |
| Exibir lista de usuários do chat      |  /list                               |
| Exibir lista de amigos                |  /mylist                             |
| Adicionar usuário à lista de amigos   |  /addtomylist <nome_do_usuario>      |
| Remover usuário da lista de amigos    |  /rmvfrommylist <nome_do_usuario>    |
| Banir usuário da sala                 |  /ban <nome_do_usuario>              |

## Outros

1. Formato da mensagem:
   1. \<IP\>:\<PORTA\>/~\<nome_usuario\>: \<mensagem\> \<hora-data\>
2. Mensagem de alerta quando um usuário se conecta
   1. <nome_usuario> entrou na sala
3. Dois usuarios nao podem se conectar com o mesmo nome
4. Usuarios amigos ganham uma tag \[amigo\]
5. Banir usuario:
   1. Servidor abre uma contagem
   2. Caso atinga mais da metade de usuarios conectados, usuario e banido
   3. Todos recebem uma mensagem: <nome_usuario> ban x/y
      1. x é o numero de votos
      2. y é o numero de votos necessarios (metade + 1)

## Simulando perda de pacotes

Perdas de pacotes podem ser simuladas alterando a variável `SEND_PROBABILITY` em `sender.py` e `receiver.py`, de acordo com qual lado se deseja simular a perda. Esta variável define a probabilidade que um pacote seja enviado com sucesso por uma máquina.

Logo com `SEND_PROBABILITY = 1`, os pacotes sempre irão ser enviados. Com `SEND_PROBABILITY = 0.5`, os pacotes serão enviados apenas 50% das vezes.

```python
# ./sender.py

class Sender:
    SEND_PROBABILITY = 0.8 # ocasiona 20% de perdas
```

O funcionamento desta simulação é definida em `common.py`:

```python
# ./common.py

# Envia pacotes via UDP. simula perdas de acordo com probability
def udt_send(...probability=1.0):
    ...
    if rand < probability:
        return self.sock.sendto(data, address)
    else:
        printc("== ! Simulando falha na transmissão ! ==", bcolors.FAIL)
        return 0
    ...
```

## Funcionamento

O cliente possui uma interface de comandos para facilitar a interação

### Detalhes sobre pacotes

Todo pacote enviado tanto pelo cliente quanto pelo servidor terá adicionado um header, indicando uma sequencia de caracteres que identifique o pacote `"HELLOPKT"`, os numeros `seq` e `ack`, e o conteudo do pacote

### Timeout

Seguindo o que é definido no RDT 3.0, o `Sender` irá iniciar um temporizador (duração padrão de 2 segundos) toda vez que um pacote for transmitido. Caso o temporizador estoure, ele será retransmitido

```python
# ./sender.py

# alterar delay padrão do temporizador
def start_timer(self, duration=2):
```

### Modificando o endereço do servidor/cliente

O cliente e servidor, por padrão, estão ambos localizados em `localhost`, nas portas `1337` e `5000`, respectivamente. Para alterar o endereço de um deles, basta modificar o código que chama o inicializador da classe de utilidades `Socket`:

```python
# ./cliente.py

# inicializar cliente na porta 1337, IP padrão (localhost)
client = Socket(port=1337)
...
```

```python
# ./servidor.py

# inicializar servidor na porta 2000, IP localhost
server = Socket(ip="localhost", port=2000)
...
```

Para alterar o destino de envio dos arquivos, basta modificar as seguintes variaveis em `cliente.py`:

```python
# ./cliente.py

...
# definir servidor para onde vao ser enviados os arquivos
server_ip = "localhost"
server_port = 5000
...
```

### Envio entre máquinas diferentes

Para testar o envio entre máquinas diferentes, certifique-se de definir o IP do servidor como `0.0.0.0`

```python
# ./servidor.py

# inicializar servidor na porta 2000, IP 0.0.0.0
server = Socket(ip="0.0.0.0", port=2000)
...
```
