import socket
import selectors
import types
import sys
import threading
import time

sel = selectors.DefaultSelector()

class ChatClient:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        self.sock = None
        self.connected = False

    def connect(self):
        """Conecta al servidor y envía username"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"Conectado a {self.host}:{self.port}")

            # Enviar username primero
            self.sock.send(self.username.encode('utf-8'))
            print(f"Username enviado: {self.username}")
            return True
        except Exception as e:
            print(f"Error conectando: {e}")
            return False

    def send_message(self, message):
        """Envía mensaje al servidor"""
        if self.connected and self.sock:
            try:
                self.sock.send(message.encode('utf-8'))
            except:
                print("Error enviando mensaje")
                self.connected = False

    def receive_messages(self):
        """Recibe mensajes del servidor en bucle"""
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if data:
                    print(data.decode('utf-8'), end='')
                else:
                    print("\nServidor desconectado")
                    self.connected = False
                    break
            except:
                self.connected = False
                break

    def start(self):
        """Inicia cliente con input de usuario"""
        if not self.connect():
            return

        # Thread para recibir mensajes
        recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
        recv_thread.start()

        # Main thread para enviar mensajes
        print("\n=== Chat activo (escribe 'quit' para salir) ===")
        while self.connected:
            try:
                msg = input()
                if msg.lower() == 'quit':
                    break
                self.send_message(msg)
            except KeyboardInterrupt:
                break

        self.sock.close()
        print("Desconectado")

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <username>")
    print("example: python chat-client.py 127.0.0.1 65432 cliente_01")
    sys.exit(1)

host, port, username = sys.argv[1], int(sys.argv[2]), sys.argv[3]
client = ChatClient(host, port, username)
client.start()
