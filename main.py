# -*- coding: utf-8 -*-
import socket
import sys
import random
import struct
import time
import re


class Tracer():

    def __init__(self) -> None:
        self.traceroute_port = 33434
        # Definimos o valor máximo da quantidade de hops.
        self.max_hops = 30


    def generate_socket_object(self, type, protocol):
        created_socket = socket.socket(
            family=socket.AF_INET,
            type=type,
            proto=protocol
        )
        return created_socket

    # Gerar socket receiver (SOCK_RAW e o protocolo ICMP).
    def generate_receiver(self, port):
        
        socket_receiver = self.generate_socket_object(socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # Variável struct de tempo para determinar o tempo de espera (segundos, microsegundos)
        timeout = struct.pack("ll", 3, 0)

        # Para que não seja aguardado por muito tempo, define-se o timeout do receiver.  
        socket_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        # O bind relaciona o socket receiver a um endereço aleatório.
        try:
            socket_receiver.bind(('', port))
        except socket.error:
            print('Não foi possível fazer a ligação com receiver socket')
        
        # Retornamos o socket receiver.
        return socket_receiver

    # Gerar socket sender (SOCK_DGRAM e o protocolo UDP).
    def generate_sender(self, ttl):
        
        socket_sender = self.generate_socket_object(socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Vamos definir o TTL no pacote UDP para ser enviado
        socket_sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        # Retornamos o socket sender
        return socket_sender

    # Assim, vamos enviar pacotes UDP e receber mensagens ICMP de Time Exceeded.

    # Função de inicialização e execução dos procedimentos de tracing
    def trace(self):
        
        # Esperamos a chamada do arquivo e a rota que deve ser um site.
        if len(sys.argv) != 2 :
            print("Erro: Por favor, especifique a rota de destino!")
            print("Ajuda: /usr/bin/python get_trace.py upe.poli.br")
            exit()

        # Selecionamos a porta entre 33434-33534 e ligamos ao bind. 
        port_chosen = self.traceroute_port


        
        # Definimos a rota que será feito o trace.
        route_to_trace = sys.argv[1]
        
        if route_to_trace[0].isdigit() == False :
            # Tentamos verificar o host da rota inserida
            print("Tentando adquirir o host da rota: '" + route_to_trace + "', por favor aguarde...")
            
            try:
                ip_of_dest = socket.gethostbyname(route_to_trace)
            except socket.error:
                print("Erro: Não foi possível adquirir o host para a rota especificada: " + socket.error)
                exit()

            print("Host: " + ip_of_dest + " encontrado com sucesso.")
        
            # Dados encontrados durante o tracing no padrão (route,host,hop)
            print("Tracing para a rota " + str(route_to_trace) + ' (' + str(ip_of_dest) + '), ' + str(self.max_hops) + " máximo de hops\n")
        else:
            ip_of_dest = route_to_trace

            # Dados encontrados durante o tracing no padrão (route,host,hop)
            print("Tracing para a rota " + ' (' + str(ip_of_dest) + '), ' + str(self.max_hops) + " máximo de hops\n")

        # Início dos procedimentos de tracing 
        string_data = ''

        # A cada TTL desejamos enviar o valor em thresh_packets, a ser contabilizado no próximo laço. 
        n_packets = 0

        # Número limite de pacotes
        thresh_packets = 3 

        for ttl in range(1, self.max_hops+1):

            string_data = ''
            for i_packets in range(thresh_packets):

                # Geramos novos receptores e remetentes.
                receiver = self.generate_receiver(port_chosen)
                sender = self.generate_sender(ttl)

                # Vamos enviar um pacote UDP para a rota na porta selecionada.
                sender.sendto(b'1024', (route_to_trace, port_chosen))

                # Registramos o tempo de envio do pacote para calcular o RTT - Round Trip Time.
                init_time = time.time()

                # Vamos armazenar a resposta ICMP
                address = None

                try:
                    # data_sent caracteriza os dados enviados. 
                    #'address[0]' é o endereço do socket que está enviando.
                    data_sent, address = receiver.recvfrom(1024)
                    
                    # Registramos o momento em que o pacote ICMP foi recebido.
                    final_time = time.time()

                # O processo resultará em erro se a resposta não puder ser recebida.
                except socket.error:
                    print("Os dados não foram recebidos.", end='')
                    pass
            
                #Concluimos fechando os sockets.
                receiver.close()
                sender.close()

                # Aumentamos o registro de pacotes enviados no TTL.
                i_packets += 1
        
                # Se o pacote enviado pelo sender for respondido por um socket.
                if address:

                    # Calculamos o RTT(round trip time)
                    rtt = round((final_time - init_time) * 1000, 2)

                    # Dados do tracing
                    if i_packets == 1:
                        string_data = (str(ttl) + ' | RTT 1º pacote: ' + str(rtt) + ' ms |')
                    elif i_packets == 2:    
                        string_data += (' RTT 2º pacote: ' + str(rtt) + ' ms |')
                    elif i_packets == 3:
                        string_data += (' RTT 3º Pacote: ' + str(rtt) + ' ms | IP do Roteador: (' + str(address[0]) + ')')
                        print(string_data)

                    # Quando o host de destino é alcançado, finaliza.
                    if address[0] == ip_of_dest:
                        break
                else:
                    print(str(ttl) + '...')




trace = Tracer()
trace.trace()