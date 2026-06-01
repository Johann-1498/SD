#    TCP Content Delivery Network
#    Author:  Justin C Presley
#    Github:  https://github.com/justincpresley
#    Contact: justincpresley@gmail.com

from argparse import ArgumentParser, SUPPRESS
import socket
import logging
import time
from utils.packet_functions import *
from utils.basic_functions import *
import threading

server_map = {}
server_map_lock = threading.Lock()

def parse_server_endpoint(value, default_port):
    raw = value.strip()
    if ":" in raw:
        ip, port_str = raw.rsplit(":", 1)
        if not validate_ip(ip):
            return None
        try:
            port = int(port_str)
        except ValueError:
            return None
        if port < 0 or port > 65535:
            return None
        return f"{ip}:{port}"
    if validate_ip(raw):
        return f"{raw}:{default_port}"
    return None

def split_server_endpoint(endpoint):
    ip, port_str = endpoint.rsplit(":", 1)
    return ip, int(port_str)

def probe_server_preference(ip, port, attempts=3, timeout=1.0):
    losses = 0
    durations = []
    for _ in range(attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.perf_counter()
        try:
            sock.connect((ip, port))
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            durations.append(elapsed_ms)
        except Exception:
            losses += 1
        finally:
            close_socket(sock)

    loss_percent = (losses / attempts) * 100.0
    avg_time_ms = sum(durations) / len(durations) if durations else 1000.0
    return (0.75 * loss_percent) + (0.25 * avg_time_ms)

def update_server_map():
    logging.info(f'---')
    global server_map
    with server_map_lock:
        endpoints = dickeys_into_list(server_map)

    for endpoint in endpoints:
        ip, port = split_server_endpoint(endpoint)
        pref = probe_server_preference(ip, port)
        with server_map_lock:
            server_map[endpoint] = pref
        logging.info(f'PingThread: {endpoint} preference={pref:.2f}')

def find_best_server_endpoint():
    global server_map
    best_endpoint = ""
    best_pref = 0.00
    with server_map_lock:
        current_map = dict(server_map)

    for key in current_map:
        if current_map[key] != 0.0:
            if best_pref != 0.00:
                if current_map[key] < best_pref:
                    best_pref = current_map[key]
                    best_endpoint = key
            else:
                best_pref = current_map[key]
                best_endpoint = key
    return best_endpoint

class ClientThread(threading.Thread):
    def __init__(self,ip,port,socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        logging.info(f'[+] New thread started for {self.ip}, {str(self.port)}')
    def run(self):
        global server_map
        best_endpoint = find_best_server_endpoint()
        while best_endpoint == "":
            logging.info(f'ClientThread: Could not select a server yet, retrying...')
            time.sleep(5)
            best_endpoint = find_best_server_endpoint()
        data = best_endpoint.encode('utf-8')
        send_packet(self.socket, form_packet(1,1,data,syn=True))
        pref = server_map.get(best_endpoint, 0.0)
        logging.info(f'Request from {self.ip} for <URL>. Redirecting to {best_endpoint}. Preference {pref}.')
        logging.info(f'Response from {best_endpoint} sending request to {self.ip}.')
        self.socket.close()
        logging.info(f'[-] Thread ended for {self.ip}, {str(self.port)}')

class PingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        logging.info(f'[+] New thread started for pinging the servers')
    def run(self):
        try:
            while self.running:
                update_server_map()
                logging.info(f'PingThread: Server Preferences are Updated')
                logging.info(f'PingThread: {server_map}')
                time.sleep(3) # in seconds how long to wait
        finally:
            pass
    def stop(self):
        self.running = False

def main():
    # Command line parser
    parser = ArgumentParser(add_help=False,description="Ping a port on a certain network")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All command line arguments
    requiredArgs.add_argument("-s","--servers",required=True,help="file that contains all server ips")
    requiredArgs.add_argument("-p","--port",required=True,type=int,help="the port the servers listens on, must be integer")
    requiredArgs.add_argument("-l","--logfile",required=True,help="where it will keep a record of actions")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All arguments
    args = vars(parser.parse_args())

    # Logging setup
    logpath = str(args["logfile"])
    logging.basicConfig(level=logging.NOTSET,filename=logpath,filemode='w',format='%(message)s')

    # Relaying ALL arguments into variables
    if args["port"] < 0 or args["port"] > 65535:
        logging.error(f'Incorrect port number {args["port"]} not in 0-65535.')
        exit()

    servers_file = args["servers"]
    port = int(args["port"])
    list_of_servers = file_into_list(servers_file)
    logging.info(f'Avaliable Servers from Log: {list_of_servers}')

    # Make the complex mapping from server list
    global server_map
    for server in list_of_servers:
        endpoint = parse_server_endpoint(server, port)
        if endpoint is not None:
            server_map[endpoint] = 0.00
        else:
            logging.warning(f'Ignoring invalid server endpoint from file: {server}')

    if len(server_map) == 0:
        logging.error('No valid server IPs were provided in servers file.')
        return

    # Create a thread to ping and manage servers
    pthread = PingThread()
    pthread.start()

    # Load Balancer Setup
    logging.info(f'LoadBalancer: starting socket')
    sourceSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sourceSock.bind(('',port))

    logging.info(f'LoadBalancer: socket listening')
    sourceSock.listen(10)

    # Communications
    cthreads = []
    while True:
        try:
            (clientsock, (ip, port)) = sourceSock.accept()
            newthread = ClientThread(ip, port, clientsock)
            newthread.start()
            cthreads.append(newthread)
        except KeyboardInterrupt:
            break

    pthread.stop()
    pthread.join()
    for t in cthreads:
        t.join()
    close_socket(sourceSock)

if __name__ == '__main__':
    main()
