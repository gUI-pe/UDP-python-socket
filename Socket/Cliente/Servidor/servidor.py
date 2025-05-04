import socket
import os
import threading
from hashlib import md5
import sys
class Cliente:
    def __init__(self):
        self.client_address = ''
        self.data = ''
        self.partes= {}
        #self.partes = []
        self.part_number = 0  # Iniciar com 0
    
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((host, port))
        self.buffer_size = 1024  # Tamanho do buffer para cada parte
        self.local_path = os.path.dirname(os.path.abspath(__file__))
        self.FOTO1PNG = os.path.join(self.local_path, "iteracao.txt")
        self.FOTO2PNG = os.path.join(self.local_path, "iteracao2.txt")
        self.clientes = {}  # Dicionário para armazenar clientes

    def send_file_part(self, cliente: Cliente):
        print(f"Requisição do cliente {cliente.client_address}: {cliente.data}")
        print(cliente.data)
        if cliente.data == 'GET /foto1':
            file_path = self.FOTO1PNG
        elif cliente.data == 'GET /foto2':
            file_path = self.FOTO2PNG
        elif not cliente.data.startswith("RESEND"):
            mensagem = "Arquivo não encontrado!"
            checksum_encoded = "13121sf#@za"
            mensagem_completa = f"{mensagem}#{checksum_encoded}"
            self.server.sendto(mensagem_completa.encode(), cliente.client_address)
            return
        if cliente.data.startswith("RESEND"):
            mensagem = cliente.data.split(",")
            mensagem = int(mensagem[1])
            for cliente.part_number, data_to_send in cliente.partes.items():
                if int(cliente.part_number) == mensagem:
                    data = data_to_send
                    self.server.sendto(data.encode(), cliente.client_address)
                    return
        listaDasPartes = []
        with open(file_path, "r") as file:
            while True:
                parte = file.read(self.buffer_size-100)
                if not parte:
                    break  
                checksum = md5(parte.encode()).hexdigest()
                checksum = checksum[:16]
                data_to_send = f"{cliente.part_number}#{parte}#{checksum}"
                cliente.partes[cliente.part_number] = data_to_send
                print(cliente.part_number)
                cliente.part_number += 1
                self.server.sendto(data_to_send.encode(), cliente.client_address)
        print('Numero total de partes enviadas: ' + str(cliente.part_number))
        fim = "END" 
        self.server.sendto(fim.encode(), cliente.client_address)

    def start(self):
        print("Servidor UDP rodando...")
        while True:
            try:
                data, client_address = self.server.recvfrom(self.buffer_size)
                if(data.decode().startswith("GET")):
                    if client_address not in self.clientes:
                        novo_cliente = Cliente()
                        novo_cliente.client_address = client_address
                        novo_cliente.data = data.decode()
                        self.clientes[client_address] = novo_cliente
                        client_handler = threading.Thread(target=self.send_file_part, args=(self.clientes[client_address],))
                        client_handler.start()
                elif data.decode().startswith("RESEND"):
                    self.clientes[client_address].data = data.decode()
                    self.send_file_part(self.clientes[client_address])
            except ConnectionResetError:
                print(f"Conexão fechada pelo cliente {client_address}")
                continue

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12345
    server = Server(host, port)
    server.start()
