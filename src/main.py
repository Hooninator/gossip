import socket
import re
import threading
import argparse
import time
import random

from collections import defaultdict


blacklist = []
connections = {}
ip_counts = defaultdict(list)
local_digit = -1 
myhost = "128.84.213.13"
myport = "5678"
myid = f"{myhost}:{myport}"
msg_limit = 9000
maxlines = 256
conn_lock = threading.Lock()
evil_active = False


def pick_random_connection():
    global connections

    n = len(connections)

    if n==0:
        return "empty", ""

    lc = list(connections)

    while True:
        idx = random.randint(0, n-1)
        k = lc[idx]
        if k != myid:
            host, port = split_id(k)
            return host, port
        elif k==myid and n==1:
            return "empty", ""


def state_str():
    global connections
    s = ""
    for addr in connections:
        t,d = connections[addr]
        if addr == myid and int(d) == -1:
            continue
        s += f"{addr},{t},{d}\n"
    return s[:-1] # Exclude the last newline


def evil_mode(host, port):
    global evil_active
    evil_active = True


def open_conn(host, port):

    hostport = f"{host}:{port}"

    if hostport in blacklist:
        print(f"Blacklisted node: {hostport}")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError as e:
            print(f"Could not connect to {hostport}. Error: {e}")
            blacklist.append(hostport)
            return
        res = s.recv(msg_limit)
        parse_response(res)


def parse_response(res):
    global connections

    res = res.decode()

    if res == '':
        return

    lines = res.strip().split("\n")

    conn_lock.acquire()
    i = 0
    try:
        for line in lines:

            if i > maxlines:
                break

            i += 1

            s = line.split(",")
            hostport, t, d = s


            # Only update if newer timestamp
            dold = 11
            if hostport in connections:
                told = connections[hostport][0]
                dold = connections[hostport][1]
                if told >= int(t) or int(time.time()) < int(t):
                    continue


            ip_counts[hostport].append(int(t))
            connections[hostport] = (int(t), int(d))

            if len(ip_counts[hostport]) > 3:
                ip_counts[hostport].sorted()
                ip_counts[hostport].pop(0)

            if int(dold) != int(d):
                print(f"{hostport} --> {d}")

    except Exception as e:
        print(f"Invalid response {res}")
    conn_lock.release()



def check_newconn(usr_input):
    return re.match(r"^\+\d+(?:\.\d+){3}:\d+$", usr_input) is not None

def check_update_digit(usr_input):
    return re.match(r"\d$", usr_input)

def check_question(usr_input):
    return re.match(r"\?$", usr_input)

def check_minus(usr_input):
    return re.match(r"\-$", usr_input)

def split_id(_id):
    hostport = _id.split(":")
    host, port = hostport[0], int(hostport[1])
    return host, port

def parse_input(usr_input):
    global local_digit, connections

    if check_newconn(usr_input):
        # Case 1: Add new connection

        inp = usr_input[1:]
        host, port = split_id(inp)
        open_conn(host, port)


    elif check_update_digit(usr_input):
        # Case 2: Update local digit

        conn_lock.acquire()
        connections[myid] = (int(time.time()), int(usr_input))
        conn_lock.release()

        new_digit = int(usr_input)

        if new_digit != local_digit:
            local_digit = int(usr_input)
            print(f"{myid} --> {local_digit}")

    elif check_minus(usr_input):
        host, port = pick_random_connection()
        evil_mode(host, port)


    elif check_question(usr_input):
        for connection in connections:
            print(f"{connection} --> {connections[connection][1]}")

    else:
        # Invalid user input, do nothing
        print(f"Invalid user input {usr_input}")


def listen_loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        # Open my socket
        s.bind((myhost, int(myport)))
        s.listen()

        while True:
            # Block until I receive a new connection
            conn, addr = s.accept()

            # Received new connection, send them a message
            if evil_active:
                payload = f"0000.00.00.00:00,1,1\n"
            else:
                payload = state_str()
            with conn:
                conn.sendall(payload.encode())
            

def gossip_loop():
    while True:

        time.sleep(3.0)

        host, port = pick_random_connection()

        if host == "empty":
            continue

        open_conn(host, port)



def hook():

    # Listen for incoming connections
    t1 = threading.Thread(target=listen_loop)

    # Every 3 seconds, gossip with random node
    t2 = threading.Thread(target=gossip_loop)

    t1.start()
    t2.start()

    # Parse user input in a loop
    while True:
        usr_input = input()
        parse_input(usr_input)
        

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--port", type=str, required=True)
    args = parser.parse_args()

    myhost = args.host
    myport = args.port
    myid = f"{myhost}:{myport}"


    hook()

