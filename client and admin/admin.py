import getpass
import socket
import sys
import re

ADDR = ('localhost', 50007)
FORMAT = 'utf-8'
HEADER = 5

ADMIN = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def disconnect():
    send_msg('DISCONNECT')
    sys.exit(0)


def send_msg(msg: str):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    ADMIN.send(send_length)
    ADMIN.send(message)


def send_preordained_msg(msg: str):
    ADMIN.send(msg.encode(FORMAT))


def get_msg() -> str:
    massage_length = int(ADMIN.recv(HEADER).decode(FORMAT))
    return ADMIN.recv(massage_length).decode(FORMAT)


def get_preordained_msg(massage_length: int = 1) -> str:
    return ADMIN.recv(massage_length).decode(FORMAT)


def user_name_validation(user_name: str,
                         throw_warning: bool = True) -> bool:
    user_name_pattern = r'^[a-zA-Z0-9_-]{3,20}$'

    if not re.match(user_name_pattern, user_name):
        if throw_warning:
            print('you can use letters of the Latin alphabet, numbers and symbols _ - ')
            print('name length must not be less than 3 or more than 20 characters')
        return False
    return True


def user_creation_request():
    send_msg('create user')

    # username
    while True:
        user_name = input('user name: ')
        if not user_name_validation(user_name):
            continue

        send_msg(user_name)
        user_exist = get_preordained_msg()
        if user_exist == 'Y':
            break
        else:
            print('user exist, please enter other user name')

    # password
    while True:
        user_password = getpass.getpass('password: ')

        if len(user_password) > 20 or len(user_password) < 6:
            print('valid password length from 6 to 20 characters')
        else:
            break

    send_msg(user_password)

    print('user created!')


def delete_user_request():
    send_msg('delete')
    while True:
        account_number = input('enter account number: ')
        if not account_number.isdigit() and not len(account_number) <= 8:
            print('The transfer number must contain 8 digits')
            continue

        send_msg(account_number)
        if get_preordained_msg() == 'N':
            print('User is not found!')
            continue

        verdict = input('Are you sure you want to delete this user?\n'
                        'y/n: ').lower()
        if verdict != 'y':
            send_preordained_msg('N')
            break
        print(get_msg())


def change_user_data_request():
    send_msg('change data')

    find_user_by_menu = {
        '1': 'user name',
        '2': 'account number',
    }

    while True:
        find_by = input(f'1: {find_user_by_menu["1"]}\n'
                        f'2: {find_user_by_menu["2"]}\n'
                        f'find user by: ')

        if find_by not in find_user_by_menu:
            print('No such command exist, try again')
            continue
        send_msg(find_user_by_menu[find_by])

        find = input(f'enter {find_user_by_menu[find_by]}: ')
        send_msg(find)

        if get_preordained_msg() == 'Y':
            break
        else:
            print('User is not found!')

    change_user_by_menu = {
        '1': "password",
        '2': "amount of money"
    }
    while True:
        change_by = input(f'\n1:{change_user_by_menu["1"]}\n'
                          f'2:{change_user_by_menu["2"]}\n'
                          'change: ')

        if change_by in change_user_by_menu:
            send_msg(change_user_by_menu[change_by])
            break
        else:
            print('No such command exist, try again')
            continue

    while True:
        change = input(f'enter new {change_user_by_menu[change_by]}: ')

        if change_by == '1':
            if len(change) > 20 or len(change) < 6:
                print('valid password length from 6 to 20 characters')
                continue
        else:
            if not change[1:].isdigit() and change[0] != '-':
                print('enter only digits')
                continue
        send_msg(change)
        break


menu = {
    '!create': user_creation_request,
    '!delete': delete_user_request,
    '!change': change_user_data_request,
    '!disc': disconnect,
}

show_menu = '!create: user creation\n' \
            '!delete: delete user\n' \
            '!change: change user data\n' \
            '!disc: disconnect'
if __name__ == '__main__':
    try:
        ADMIN.connect(ADDR)
    except ConnectionRefusedError:
        print('server can be turned off or changed address\n'
              'please try again later')
        getpass.getpass('press enter')
        sys.exit(0)
    try:
        send_msg('admin')

        while True:
            send_msg(input('login: '))
            if get_preordained_msg() == 'Y':
                break
            print('wrong login')

        while True:
            send_msg(getpass.getpass('password: '))
            if get_preordained_msg() == 'Y':
                break
            print('wrong password')

        print(' text `!help` if your first time in our service:)')
        while True:
            request = input('enter the command: ')

            if request == '!help':
                print(show_menu)
            elif request in menu:
                menu[request]()
            else:
                print('No such command exist, try again')

    except ConnectionResetError:
        print('server can be turned off or changed address\n'
              'please try again later')
        getpass.getpass('press enter')
