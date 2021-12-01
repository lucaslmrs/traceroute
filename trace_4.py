#!/usr/bin/env python3
# -- coding: utf-8 --

import socket
import time

#alvo = input('Digite end. IP, destino: ')
alvo = '200.133.2.18'
#ttl = int(input('Digite o TTL pretendido: '))

ssnd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #enviar UDP
##

srcv = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1) #receber só ICMP
srcv.bind(("", 33434))
srcv.settimeout(1)

for ttl in range(1,31):
    ssnd.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    listadetemposarmazenados=[]
    end_alcancado = ''
    buf = b''

    print("-"*50)
    print('TTL = ',ttl)

    for count in range(1,4):

        ssnd.sendto(b'', (alvo,33433))
        tempo_inicial = time.time()

        try:
            buf = srcv.recvfrom(1024)
            tempo_final = time.time()

            listadetemposarmazenados.append(round((tempo_final - tempo_inicial)*1000, 2))

        except socket.timeout:
            print('tempo esgotado')

    if(buf):

        end_alcancado= buf[1]

        print('chegou no IP: ' + end_alcancado[0])

        if len(listadetemposarmazenados) >= 1 :
            print('pacote 1:' + str(listadetemposarmazenados[0])+'ms')
        if len(listadetemposarmazenados) >= 2 :
            print('pacote 2:' + str(listadetemposarmazenados[1])+'ms')
        if len(listadetemposarmazenados) >= 3 :
            print('pacote 1:' + str(listadetemposarmazenados[2])+'ms')

    else:
        print('As tres tentativas falharam. endereço não encontrado')

    print()
    listadetemposarmazenados=[]


ssnd.close()
srcv.close()