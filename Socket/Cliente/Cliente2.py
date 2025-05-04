import socket
import os
from hashlib import md5
import sys
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
IMAGEM_FILE = "arquivo2.txt"
BUFFER_SIZE = 1024

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)  # tempo limite de 5 segundos para receber algo

    escolha = input("Escolha 1 para o arquivo de 32MB, e 2 para arquivo de 9MB: ")
    escolha = int(escolha)
    parte_a_corromper = input("Packet loss? ")
    if escolha == 1:
        file_request = "GET /foto1"
    elif escolha == 2:
        file_request = "GET /foto2"
    else:
        file_request = "GET /inexistente"
    
    partes_descartadas = []
    while True:
        client.sendto(file_request.encode(), (SERVER_IP, SERVER_PORT))
        partes = []
        i = 0
        while True:
            try:
                data, _ = client.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                print("Tempo limite excedido esperando resposta do servidor.")
                client.close()
                return
            
            #data, _ = client.recvfrom(BUFFER_SIZE)

            mensagem_texto = data.decode(errors="ignore")
            if mensagem_texto.startswith("ERRO"):
                print("Erro recebido do servidor:", mensagem_texto)
                client.close()
                return
        
            if data.decode() == "END":
                if len(partes_descartadas) > 0:
                    print("Solicitando reenvio de partes:", partes_descartadas)
                    mensagem = 'RESEND,' + str(partes_descartadas[0])
                    client.sendto(mensagem.encode(), (SERVER_IP, SERVER_PORT))
                    recuperaPartes(client, partes_descartadas, partes)
                else:
                    num_parteDescartada = None
                    partes_descartadas = None
                    cria_arquivo(partes,num_parteDescartada,partes_descartadas)
                client.close()
                return 0 
            parts = data.split(b'#')
            num_parte = int(parts[0])
            parte = parts[1] 
            checksum_received = parts[2]
            #checksum_calculado = md5(parte).hexdigest()
            #checksum_calculado = checksum_calculado[:16].encode()
            if parte_a_corromper == str(num_parte):
                parte = b'corrompido'
                print("Parte", num_parte, "corrompida!")

            checksum_calculado = md5(parte).hexdigest()
            checksum_calculado = checksum_calculado[:16].encode()

            if checksum_received != checksum_calculado:
                num_parteDescartada = num_parte
                print("Erro de checksum na parte", num_parte)
                partes_descartadas.append(num_parte)
            else:
                print("Parte", num_parte, "recebida com sucesso!")
                partes.append(parte)
            i += 1
def recuperaPartes(client: socket.socket, partes_descartadas: list, partes: list):
        try:
            mensagem, _ = client.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            print("Tempo limite excedido esperando resposta do servidor.")
            client.close()
            return
        
        mensagem, _ = client.recvfrom(BUFFER_SIZE)
        partes_split = mensagem.split(b"#")
        client.close()
        num_parteDescartada = int(partes_split[0])
        print("o pacote que foi perdido: " + str(num_parteDescartada) + " foi recebido com sucesso")
        parte = partes_split[1]
        checksum_received = partes_split[2]
        checksum_calculado = md5(parte).hexdigest()
        checksum_calculado = checksum_calculado[:16]
        partes_descartadas.clear()
        partes_descartadas.append(parte)
        cria_arquivo(partes, num_parteDescartada, partes_descartadas)
        
def cria_arquivo(partes, num_parteDescartada, partes_descartadas):
    with open(IMAGEM_FILE, "wb") as file:
        i = 0
        for parte in partes:
            parte = parte
            if i != num_parteDescartada:
                file.write(parte)
            else:
                file.write(partes_descartadas[0])
                file.write(parte)
                i += 1
            i += 1
        print("Numero de partes recebidas: " + str(i))

if __name__ == "__main__":
    main()
