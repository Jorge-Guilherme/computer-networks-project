# Chat baseado em Arquivos com UDP

## 📌 Sobre o Projeto
Este projeto implementa um **chat baseado em arquivos** utilizando **UDP** em Python. Os clientes podem se conectar a um servidor, trocar mensagens e compartilhar arquivos **.txt**. O servidor gerencia a comunicação entre os clientes, retransmitindo mensagens e notificando eventos de entrada e saída da sala.

## Equipe 4
- **Diego Davis Melo** `<ddm>`
- **Jorge Guilherme Luna de Vasconcelos Cabral** `<jglvc>`
- **José Janailson de Arruda Cunha** `<jjac>`

---

# Parte 1: Implementação do Chat com UDP

## 📜 Funcionalidades
✅ Envio e recebimento de mensagens via UDP utilizando arquivos **.txt**  
✅ Notificação quando um novo usuário entra na sala  
✅ Notificação quando um usuário sai da sala  
✅ Troca de arquivos entre os usuários  
✅ Suporte a múltiplos clientes simultaneamente  

## 🚀 Tecnologias Utilizadas
- **Python 3**
- **Sockets UDP** para comunicação
- **Threads** para processamento assíncrono

---

## 📂 Estrutura do Projeto
```
📁 chat_udp
│-- 📁 files_server         # Armazena arquivos recebidos pelo servidor
│-- 📁 files_client         # Armazena arquivos recebidos pelos clientes
│-- 📁 test_files           # Arquivos testes para enviar
│-- 📄 servidor.py          # Código do servidor
│-- 📄 cliente.py           # Código do cliente
│-- 📄 common.py            # Módulo comum com funções de comunicação UDP
│-- 📄 README.md            # Documentação do projeto
```

---

## 📌 Como Executar

### **1️⃣ Executar o Servidor**
Abra um terminal e execute:
```bash
python servidor.py
```
Isso iniciará o servidor na porta **5000**, pronto para receber conexões de clientes.

### **2️⃣ Executar Clientes**
Para cada cliente, abra um novo terminal e execute:
```bash
python cliente.py
```
Cada cliente terá seu próprio ambiente de chat.

---

## 🎯 Comandos Disponíveis
Dentro do chat, os usuários podem usar os seguintes comandos:

| Comando                          | Descrição                                    |
|----------------------------------|--------------------------------------------|
| `hi, meu nome eh <nome>`        | Conecta ao chat com um nome de usuário   |
| `/bye`                            | Sai do chat e notifica os outros usuários |

---

## 📌 Exemplo de Uso
### **Entrada de Usuários**
```
> hi, meu nome eh messi
192.168.1.10:54321/~messi entrou na sala.
```
```
> hi, meu nome eh ruy
192.168.1.11:53421/~ruy entrou na sala.
```

### **Envio de Mensagens**
```
> Olá, pessoal!
192.168.1.10:54321/~messi: Olá, pessoal! 14:20:30 18/02/2025
```

### **Saída do Usuário**
```
> /bye
Saindo do chat...
192.168.1.10:54321/~messi saiu da sala.
```

---

# Parte 2: Requisitos e Especificações

## 📌 Requisitos do Projeto
O chat UDP foi desenvolvido com base nos seguintes requisitos:

1. **Arquitetura Cliente-Servidor:** O servidor deve gerenciar conexões e troca de mensagens entre clientes.
2. **Protocolo de Comunicação:** Utiliza UDP para envio de mensagens e arquivos.
3. **Gerenciamento de Arquivos:** Os arquivos de mensagens devem ser armazenados temporariamente e manipulados pelos clientes e servidor.
4. **Controle de Conexões:** O servidor deve notificar a entrada e saída de clientes na sala de bate-papo.
5. **Simultaneidade:** Deve permitir múltiplos clientes se comunicando ao mesmo tempo.

## 📂 Estrutura dos Arquivos
Os arquivos utilizados no chat seguem a seguinte organização:

- **Mensagens:** As mensagens são salvas em arquivos `.txt`, cada cliente lê e grava mensagens.
- **Armazenamento de Arquivos:** O servidor mantém os arquivos enviados pelos clientes para compartilhamento.
- **Logs:** O servidor registra eventos como conexões e desconexões de usuários.

## 📌 Melhorias Futuras
- Implementação de criptografia para mensagens e arquivos.
- Suporte a envio de arquivos de outros formatos além de `.txt`.
- Interface gráfica para facilitar a usabilidade.

---

## 📢 Conclusão
Este projeto demonstrou como um chat UDP pode ser implementado usando Python, permitindo a comunicação via mensagens e arquivos. Futuramente, melhorias poderão ser feitas para tornar a solução mais segura e funcional.

