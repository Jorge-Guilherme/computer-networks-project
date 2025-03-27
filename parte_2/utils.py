import re


def pretty_print(msg, gutter="|", roof="-", floor="-"):
    msg = gutter + " " + msg + " " + gutter
    printc(len(msg) * roof, bcolors.HEADER)
    printc(msg, bcolors.HEADER)
    printc(len(msg) * floor, bcolors.HEADER)

def print_elapsed(tic, toc, id=""):
    printc(f"# [{id}]: {toc - tic}s", bcolors.OKCYAN)

def printc(msg, color=None):
    if color:
        print(f"{color}{msg}{bcolors.ENDC}")
    else:
        print(msg)

class bcolors:
    HEADER = '\033[95m',
    OKBLUE = '\033[94m',
    OKCYAN = '\033[96m',
    OKGREEN = '\033[92m',
    WARNING = '\033[93m',
    FAIL = '\033[91m',
    ENDC = '\033[0m',
    BOLD = '\033[1m',
    UNDERLINE = '\033[4m'

def extract_msg(msg):
    # regex para extrair endereço, nome e mensagem de uma mensagem
    reg = r'(\d+\.\d+\.\d+\.\d+:\d+)\/~(.+): (.+) <\d+:\d+:\d+, \d+/\d+/\d+>'

    match = re.search(reg, msg)
    
    if match:
        # extrair nome e mensagem
        address = match.group(1)
        username = match.group(2)
        message = match.group(3)
        
        return (address, username, message)
    else:
        return (None, None, None)
    
def extract_msg_server(msg):
    reg = r'(.+): (.+)'

    match = re.search(reg, msg)

    if match:
        username = match.group(1)
        message = match.group(2)

        return (username, message)
    else:
        return (None, None)
    
def broadcast_msg(connected_users, sender, sender_address, msg, include_sender=False):
    for client in connected_users:
        if include_sender or connected_users[client] != sender_address:
            sender.rdt_send(msg.encode(), connected_users[client])