import socket
import threading
import queue
import random
import time

messages = queue.Queue()
clients = []
names = {}

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

def recieve():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass

def broadcast():
    day_start = time.time()
    mafia_chosen = False
    day_phase_duration = time.time()+60
    night_phase_duration = time.time()+10
    phase_start = time.time()
    while True:
        if not mafia_chosen and len(clients) >= 3:
            mafia = random.sample(list(names.values()),1)[0]
            for key, value in names.items():
                if value == mafia:
                    server.sendto("You are the mafia!".encode(), key)
            mafia_chosen = True


        while day_start < night_phase_duration:
            elapsed = time.time() - phase_start
            for key, value in names.items():
                if value == mafia:
                    server.sendto("Choose who to kill: ".encode(), key)
            if elapsed < night_phase_duration:
                night_phase = False
                day_start = time.time()





        while  day_start < day_phase_duration:
            elapsed_time = time.time() -  day_start
            day_phase = True
            if elapsed_time < day_phase_duration:
                message, addr = messages.get()
                print(message.decode())
                if addr not in clients:
                    clients.append(addr)
                for client in clients:
                    try:
                        if message.decode().startswith("TAG:"):
                            name = message.decode()[message.decode().index(":")+1:]
                            names[addr] = name
                            server.sendto(f"{name} joined!".encode(), client)
                        else:
                            server.sendto(message, client)
                    except:
                        clients.remove(client)
            day_phase = False
            night_phase = True


t1 = threading.Thread(target=recieve)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()



