import socket
import threading
import queue
import random
import time

messages = queue.Queue()
clients = []
names = {}
kills = []
votes = {}

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
    mafia_chosen = False
    day_deadline = time.time() + 50
    night_deadline = time.time() + 20
    phase = "DAY"
    msg_sent = False

    while True:
        now = time.time()
        #check if minimum players are present
        if not mafia_chosen and len(clients) >= 3:
            mafia = random.sample(list(names.values()),1)[0]
            for key, value in names.items():
                if value == mafia:
                    server.sendto("You are the mafia!".encode(), key)
                    mafia_addr = key
            mafia_chosen = True

        #night phase logic
        if phase == "NIGHT":
            if not msg_sent:
                for key, value in names.items():
                    if value == mafia:
                        server.sendto("Choose who to kill: ".encode(), key)
                msg_sent = True
            if  not messages.empty():
                msg, address = messages.get()
                if address == mafia_addr:
                    target = msg.decode().strip()
                    target = target.split(":")[1].strip()
                    if target in names.values():
                        kills.append(target)
                        server.sendto(f"Target {target} confirmed".encode(), address)
                    else:
                        server.sendto(f"[{target}] is not a user.".encode(), address)
                        print(f"target is type {type(target)}")

            #check timer
            if now >= night_deadline:
                phase = "DAY"
                for client in clients:
                    server.sendto("The sun rises...".encode(), client)
                day_deadline = time.time() + 30

        #day phase logic
        if phase == "DAY":  # add check for day phase
            # broadcasting messages
            if not messages.empty():
                message, addr = messages.get()
                print(message.decode())
                if addr not in clients and message.decode().startswith("TAG:"):
                    clients.append(addr)
                for client in clients:
                    try:
                        if message.decode().startswith("TAG:"):
                            name = message.decode()[message.decode().index(":") + 1:]
                            names[addr] = name
                            server.sendto(f"{name} joined!".encode(), client)
                        #voting logic
                        elif message.decode().split(":")[1].strip().startswith("voting"):
                            voted = message.decode().split("voting")[1].strip()
                            if voted in names.values():
                                votes[voted] = votes.get(voted,0) +1
                                server.sendto(f"You have voted {voted}".encode(), key)


                                server.sendto(f"Someone has voted!".encode(), key)
                                print(votes)

                        else:
                            server.sendto(message, client)
                    except:
                        if client:
                            clients.remove(client)
                            print("reached except block")




            #check who got killed
            if kills:
                victim = kills[-1]
                for client in clients:
                    server.sendto(f"Oh no... Our friend {victim} got killed.".encode(), client)
                for key, value in names.items():
                    if value == victim:
                        clients.remove(key)
                kills.clear()

            #check timer
            if now >= day_deadline:
                if votes:
                    player_voted = max(votes, key=votes.get)
                    for key, value in names.items():
                        if value == player_voted:
                            server.sendto("You have been voted!".encode(), key)
                            time.sleep(0.2)
                            clients.remove(key)
                phase = "NIGHT"
                for client in clients:
                    server.sendto("The sun sets... Mafia, wake up!".encode(), client)
                msg_sent = False
                night_deadline = time.time() + 10



t1 = threading.Thread(target=recieve)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()
