import threading
import requests
import time

def make_request(client_id):
    url = f"https://rabbit.rvaldiviase.me/rpc_call/mensaje_cliente_{client_id}"
    print(f"Cliente {client_id} enviando request a {url}...")
    start_time = time.time()
    try:
        response = requests.get(url)
        end_time = time.time()
        print(f"Cliente {client_id} recibió respuesta: '{response.text}' en {end_time - start_time:.2f} segundos")
    except Exception as e:
        print(f"Cliente {client_id} error: {e}")

threads = []
for i in range(1, 4):
    t = threading.Thread(target=make_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Prueba con 3 clientes completada.")
