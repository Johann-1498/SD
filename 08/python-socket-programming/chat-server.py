import selectors
import socket
import types
import sys
import threading
from datetime import datetime

sel = selectors.DefaultSelector()
clients = {}  # conn -> {username, addr}
audit_lock = threading.Lock()

def log_audit(message):
    """Escribe mensaje al log de auditoría con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with audit_lock:
        with open("audit.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    print(f"[AUDIT] {message}")

def broadcast_message(message, sender_conn=None):
    """Envía mensaje a todos los clientes conectados excepto al remitente"""
    for conn in list(clients.keys()):
        if conn != sender_conn:
            try:
                conn.send(message.encode('utf-8'))
            except:
                log_audit(f"Error sending to {clients[conn]['username']}")

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    log_audit(f"CONNECTION: {addr} connected")

    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'', username=None)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                message = recv_data.decode('utf-8').strip()

                # Primero username si es nueva conexión
                if data.username is None:
                    data.username = message
                    clients[sock] = {'username': message, 'addr': data.addr}
                    log_audit(f"USER: {message} registered from {data.addr}")

                    # Notificar a todos
                    broadcast_message(f"[SYSTEM]: {message} se ha unido al chat", sock)
                    sock.send(f"Bienvenido {message}! Estás conectado.\n".encode('utf-8'))
                else:
                    # Mensaje normal con formato [username]: mensaje
                    formatted = f"[{data.username}]: {message}"
                    print(formatted)
                    log_audit(f"MESSAGE: {data.username} from {data.addr}: {message}")

                    # Broadcast a todos los clientes
                    broadcast_message(formatted, sender_conn=sock)
            else:
                # Cliente desconectado
                username = clients.get(sock, {}).get('username', 'Unknown')
                log_audit(f"DISCONNECT: {username} from {data.addr}")

                broadcast_message(f"[SYSTEM]: {username} ha salido del chat")

                sel.unregister(sock)
                sock.close()
                if sock in clients:
                    del clients[sock]
        except Exception as e:
            log_audit(f"ERROR: {e}")
            if sock in clients:
                sel.unregister(sock)
                sock.close()
                del clients[sock]

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print("Chat server listening on", (host, port))
log_audit(f"SERVER: Started on {host}:{port}")

lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("\ncaught keyboard interrupt, exiting")
    log_audit("SERVER: Shutdown requested")
finally:
    sel.close()
