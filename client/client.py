import socket as sock
import configparser
import re

config = configparser.ConfigParser() 
config.read("../config.ini") 


UDPsocket = sock.socket(sock.AF_INET, sock.SOCK_DGRAM) 

def fragmentation(data):
    fragments = []
    fragment_number = 1
    while data:
        fragment = data[ :int(config['UDP']['max_size'])]

        # При фрагментации к сообщению в конце добавляется ~<номер фрагмента>
        fragments.append(fragment + f'~{fragment_number}') 

        fragment_number += 1
        data = data[int(config['UDP']['max_size']): ]
    return fragments

def send_fragmentation_data(fragments):
    for fragment in fragments:
        UDPsocket.sendto(str.encode(fragment), (config['UDP']['host'], int(config['UDP']['port'])))
    return

def feed(data):
    match = re.fullmatch(r'@\w+ - \w+~', data)
    if match:
        print('Sending data...')
        if len(data) > int(config['UDP']['max_size']):
            fragmentated_data = fragmentation(data)
            send_fragmentation_data(fragmentated_data)
            return True
        UDPsocket.sendto(str.encode(data), (config['UDP']['host'], int(config['UDP']['port'])))
        return True
    print('Incorrect request. The template: @username - food_name~')
    return False

def main():
    print('Hello, this is a cat! You can feed me by send UDP Datagram in format @username - food_name~!\n')
    response_data = ''
    while True:
        if response_data in ['Ignored by the Cat', 'Eaten by the Cat', '']:
            data = input('Enter data: ')
            if not feed(data):
                continue
        response_data, server_socket = UDPsocket.recvfrom(1024)
        response_data = response_data.decode()
        server_ip, server_port = server_socket
        print(f'Response from {server_ip}:{server_port}: ', response_data)    

if __name__ == '__main__':
    main()