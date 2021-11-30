#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

#alvo = input('Digite end. IP, destino: ')
alvo = '200.133.2.18'
ttl = int(input('Digite o TTL pretendido: '))

ssnd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #enviar UDP
ssnd.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

srcv = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1) #receber só ICMP
srcv.bind(("", 33434))

ssnd.sendto(b" ", (alvo, 33434)) #porta do Traceroute (TCP e UDP) #####a bytes-like object is required, not 'str'
print('pacote enviado ...')
buf = srcv.recvfrom(2048)
print('pacote recebido ...', buf)
S = buf[0]
print('Maquina remota: ', buf[1])

if ord(S[9]) == 1:
    print('Protocolo: ', ord(S[9]))
    print('TipoIcmp', ord(S[20])) #deve ser 11
    print('CodIcmp', ord(S[21])) #deve ser 0
    print('IdIcmp', ord(S[24]), ord(S[25]))
    print('SeqNo', ord(S[26]), ord(S[27]))
    print('Maquina remota: ', buf[1])
    # break

ssnd.close()
srcv.close()

