import threading
import socket
import random
import json

ADDR = ('localhost', 50007)
FORMAT = 'utf-8'
HEADER = 5
ACCOUNTS_DATA = r'Server\Accounts.json'

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind((ADDR))


def send_msg(conn, msg: str):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    conn.send(send_length)
    conn.send(message)


def send_preordained_msg(conn, msg: str):
    conn.send(msg.encode(FORMAT))


def get_msg(conn) -> str:
    massage_length = int(conn.recv(HEADER).decode(FORMAT))
    return conn.recv(massage_length).decode(FORMAT)


def get_preordained_msg(conn, massage_length: int) -> str:
    return conn.recv(massage_length).decode(FORMAT)


def find_user(find_by: str, find):
    with open(ACCOUNTS_DATA) as f:
        data = json.load(f)
    user = [user for user in data["Users"] if user[find_by] == find]
    if user:
        return user[0]
    else:
        return None


def create_user(conn, addr):
    # username
    while True:
        user_name = get_msg(conn)
        print(f'[{addr[0]}]user name: {user_name}')

        if not find_user('userName', user_name):
            send_preordained_msg(conn, 'Y')
            break
        else:
            send_preordained_msg(conn, 'N')
    # password
    user_pass = get_msg(conn)
    # create account number
    while True:
        account_number = random.randint(10000000, 99999999)
        if not find_user('account number', account_number):
            print(f'[{addr[0]}] account number: {account_number}')
            break

    # create user
    user = {
        "userName": f"{user_name}",
        "passwd": f"{user_pass}",
        "account number": f"{account_number}",
        "amount of money": 0
    }
    # save user
    with open(ACCOUNTS_DATA) as f:
        data = json.load(f)
    data['Users'].append(user)
    with open(ACCOUNTS_DATA, 'w') as f:
        json.dump(data, f, indent=2)


def authorization_user(conn):
    user_not_found = True
    user_data = {}
    while user_not_found:
        user_name = get_msg(conn)
        user_data = find_user('userName', user_name)

        if user_data:
            send_preordained_msg(conn, 'Y')
            user_not_found = False
        else:
            send_preordained_msg(conn, 'N')

    incorrect_password = True

    while incorrect_password:
        user_password = get_msg(conn)

        if user_data['passwd'] == user_password:
            incorrect_password = False
            send_preordained_msg(conn, 'Y')
            send_preordained_msg(conn, user_data['account number'])
            send_msg(conn, str(user_data['amount of money']))
            return user_data['account number']
        else:
            send_preordained_msg(conn, 'n')


def top_up_balance(conn, account_number):
    top_up_amount = get_msg(conn)

    with open(ACCOUNTS_DATA) as f:
        users = json.load(f)
    for user in users['Users']:
        if user['account number'] == account_number:
            user['amount of money'] += int(top_up_amount)
    with open(ACCOUNTS_DATA, 'w') as f:
        json.dump(users, f, indent=2)


def send_money(conn, account_number):
    user_doesnt_exist = True
    account_number_recipient = None

    while user_doesnt_exist:
        account_number_recipient = get_preordained_msg(conn, 8)
        user_recipient = find_user('account number', account_number_recipient)
        if user_recipient:
            send_preordained_msg(conn, 'Y')
            user_doesnt_exist = False
        else:
            send_preordained_msg(conn, 'N')

    while True:
        money = get_msg(conn)
        user = find_user('account number', account_number)
        if int(money) <= user['amount of money']:
            send_preordained_msg(conn, 'Y')
            with open(ACCOUNTS_DATA) as f:
                users = json.load(f)
            for user in users['Users']:
                if user['account number'] == account_number:
                    user['amount of money'] -= int(money)
                    send_msg(conn, str(user['amount of money']))
                if user['account number'] == account_number_recipient:
                    user['amount of money'] += int(money)
            with open(ACCOUNTS_DATA, 'w') as f:
                json.dump(users, f, indent=2)
                break
        else:
            send_preordained_msg(conn, 'N')


def check_money(conn, account_number):
    send_msg(conn, str(find_user("account number", account_number)["amount of money"]))


def withdraw(conn, account_number):
    with open(ACCOUNTS_DATA) as f:
        users = json.load(f)
    for user in users['Users']:
        if user['account number'] == account_number:
            while True:
                withdraw_amount = get_msg(conn)
                if int(withdraw_amount) < user['amount of money']:
                    send_msg(conn, 'y')
                    user['amount of money'] -= int(withdraw_amount)
                    break
                else:
                    send_msg(conn, 'n')
    with open(ACCOUNTS_DATA, 'w') as f:
        json.dump(users, f, indent=2)


def handle_client(conn, addr):
    account_number = None
    connected = True

    while connected:
        msg = get_msg(conn)

        if msg == 'DISCONNECT':
            connected = False
        elif msg == 'create user':
            create_user(conn, addr)
        elif msg == 'authorization':
            account_number = authorization_user(conn)
        elif msg == 'top up':
            top_up_balance(conn, account_number)
        elif msg == 'send':
            send_money(conn, account_number)
        elif msg == 'check':
            check_money(conn, account_number)
        elif msg == 'withdraw':
            withdraw(conn, account_number)


def start():
    SERVER.listen(0)
    while True:
        conn, addr = SERVER.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(
            f'{addr} is connected\nCount of active conection {threading.active_count() - 1}\n')


print(f'server is starting...')
start()
