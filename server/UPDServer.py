import socket as sock
import configparser

config = configparser.ConfigParser() 
config.read("../config.ini") 

socket = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
socket.bind((config['UDP']['host'], int(config['UDP']['port'])))

fragmentated_messages_buffer = {}

def append_fragment(fragment, client_socket):
    # Удаление тильды и номера фрагмента
    #TODO: Если вдруг номер фрагмента двузначный, удалять надо не 2 символа
    fragment = fragment[:-2]
    if client_socket in fragmentated_messages_buffer.keys():
        # Увеличение количества принятых от клиента фрагментов на 1
        fragmentated_messages_buffer[client_socket].append(fragment) 

        # Проверка того стоит ли перед постфиксом тильда. Если да - то это завершающее сообщение
        if fragment[-1] == '~':
            full_message = ''.join(fragmentated_messages_buffer[client_socket])
            del fragmentated_messages_buffer[client_socket]
            return check_food(full_message)
    else:
        # Создание первой записи о клиенте, который отправляет фрагмент
        fragmentated_messages_buffer[client_socket] = [fragment]
    return f'The Cat is amused by #{len(fragmentated_messages_buffer[client_socket])}'

def check_food(data):
    food = data[data.index('-') + 2: data.index('~')]
    print(food)
    food_list = config['UDP']['food'].split(', ')
    if food in food_list:
        return 'Eaten by the Cat'
    return 'Ignored by the Cat'

# Формирование ответа
def form_response(decoded_data, client_socket):

    # В случае, если получили фрагмент
    if decoded_data[-1] != '~':
        return append_fragment(decoded_data, client_socket)

    # В случае, если сообщение цельное
    return check_food(decoded_data)

while True:
    data, client_socket = socket.recvfrom(1024)
    client_host, client_port = client_socket
    print(f'Recieved from: {client_host}:{client_port}\nData: {data.decode()}')
    socket.sendto(form_response(data.decode(), client_socket).encode(), (client_host, client_port))
