import socket, re, getpass, sys

ADDR = ('localhost', 50007)
FORMAT = 'utf-8'
HEADER = 5

CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_msg(msg: str):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    CLIENT.send(send_length)
    CLIENT.send(message)


def send_preordained_msg(msg: str):
    CLIENT.send(msg.encode(FORMAT))


def get_msg() -> str:
    massage_length = int(CLIENT.recv(HEADER).decode(FORMAT))
    return CLIENT.recv(massage_length).decode(FORMAT)


def get_preordained_msg(massage_length: int = 1) -> str:
    return CLIENT.recv(massage_length).decode(FORMAT)


def user_creation_request():
    user_name_pattern = r'^[a-zA-Z0-9_-]{3,20}$'

    # username
    while True:
        user_name = input('user name: ')
        if not re.match(user_name_pattern, user_name):
            print('you can use letters of the Latin alphabet, numbers and symbols _ - ')
            print('name length must not be less than 3 or more than 20 characters')
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


def user_authorization_request() -> list:
    user_not_found = True

    while user_not_found:
        user_name = input('user name: ')
        send_msg(user_name)

        if get_preordained_msg() == 'Y':
            user_not_found = False
        else:
            print('user not fount')

    while True:
        user_password = getpass.getpass('password: ')
        send_msg(user_password)

        if get_preordained_msg() == 'Y':
            return [get_preordained_msg(8), get_msg()]


def top_up_balance():
    amount = input('amount: ')

    while not amount.isdigit():
        print('please enter only numbers')
        amount = input('amount: ')
    send_msg(amount)


def send_money_request():
    pattern = r'^[0-9]{8}$'
    user_doesnt_exist = True

    while user_doesnt_exist:
        number_to_transfer = input('transfer to nb account: ')
        while not re.match(pattern, number_to_transfer):
            print('The transfer number must contain 8 digits')
            number_to_transfer = input('transfer to nb account: ')
        send_preordained_msg(number_to_transfer)
        if get_preordained_msg() == 'Y':
            user_doesnt_exist = False
        else:
            print('user not fount')

    while True:
        money = input('amount of money to transfer: ')
        if not money.isdigit():
            print('enter only numbers')
            continue
        send_msg(money)
        if get_preordained_msg() == 'Y':
            print('the transaction was successful!')
            print(f'amount of money in the account {get_msg()}')
            break
        else:
            print('not enough money to transfer')


def check_money():
    print(get_msg())


def withdraw():
    while True:
        amount = input('amount: ')
        while not amount.isdigit():
            print('please enter only numbers')
            amount = input('amount: ')
        send_msg(amount)
        if get_msg() == 'y':
            print('operation was successful')
            break
        else:
            print("you don't have enough money")


try:
    CLIENT.connect(ADDR)

    connected = True
    user = []

    print(' text `!help` if your firts time in our sevice:)')
    while connected:
        request = input('enter the command: ')
        if not user:
            if request == '!help':
                print('!create       - create an user\n'
                      '!authorization - user authorization\n'
                      '!disconnect    - disconnect from server')
            elif request == '!create':
                send_msg('create user')
                user_creation_request()
            elif request == '!authorization':
                send_msg('authorization')
                user = user_authorization_request()
                print(f'user number: {user[0]}')
                print(f'amount of money in the account {user[1]}')
            elif request == '!disconnect':
                send_msg('DISCONNECT')
                connected = False
                print('you disconnected from the server')
            else:
                print('No such command exist, try again')

        else:
            if request == '!help':
                print('!send      - send money to another user\n'
                      '!ch        - check amount of money in the account\n'
                      '!topup     - Top up your account \n'
                      '!withdraw  - withdraw funds\n'
                      '!disc - disconnect from server')
            elif request == '!send':
                send_msg('send')
                send_money_request()
            elif request == '!ch':
                send_msg('check')
                check_money()
            elif request == '!topup':
                send_msg('top up')
                top_up_balance()
            elif request == '!withdraw':
                send_msg('withdraw')
                withdraw()  # //
            elif request == '!disc':
                send_msg('DISCONNECT')
                connected = False
                print('you disconnected from the server')
            else:
                print('No such command exist, try again')
except ConnectionResetError or ConnectionResetError:
    print('server can be turned off or changed address\nplease try again later')
    sys.exit(0)
