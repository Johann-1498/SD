# INFORME.MD — Practica 17: Enterprise Service Bus (ESB) con Python

**Asignatura:** Sistemas Distribuidos
**Tema:** Integracion de aplicaciones con un Enterprise Service Bus
**Framework base:** [python-micro-esb](https://github.com/clauspruefer/python-micro-esb) (Claus Pruefer, AGPLv3)
**Fecha:** 2026-06-13

---

## 1. Descripcion y alcances del ESB

### 1.1 Que es un ESB

Un **Enterprise Service Bus** es un patron de integracion introducido en el
informe Gartner de 2002. Su proposito es desacoplar los sistemas que
intercambian informacion dentro de una arquitectura orientada a servicios
(SOA) introduciendo un intermediario (el *bus*) que se encarga de:

- **Abstraccion de servicios** — los consumidores no conocen la ubicacion
  ni el formato interno de los proveedores.
- **Enrutamiento** — distribuye los mensajes al servicio correcto.
- **Transformacion** — convierte formatos (XML <-> JSON, modelo relacional
  <-> objeto, etc.).
- **Mediacion (AAA)** — autenticacion, autorizacion y contabilidad.
- **Registry** — catalogo central de los metadatos de cada servicio.

### 1.2 Alcances de python-micro-esb

`microesb` es una implementacion ligera, OOP, del patron ESB. No pretende
competir con productos como Mule ESB, WSO2 o Apache ServiceMix; en cambio
ofrece un nucleo declarativo usable dentro de una sola aplicacion Python
para modelar y ejecutar servicios sobre multiples backends.

| Capacidad | Estado en microesb |
|---|---|
| Abstraccion / modelado declarativo de servicios | Implementado |
| Mapeo OOP <-> propiedades (XML / JSON / clase Python) | Implementado |
| Registry central (class_reference + class_mapping) | Implementado |
| Transformacion JSON jerarquica recursiva | Implementado |
| Mapeo relacional (ORM/ODM) — PostgreSQL, MongoDB | Implementado via ejemplos |
| Routing a metodos definidos por el usuario | Implementado (`router.ServiceRouter`) |
| Documentacion auto-generada | En progreso |
| Web dashboard | En progreso |

### 1.3 Nucleo del framework

El modulo `microesb.py` expone cuatro clases principales:

- **`ClassHandler`** — nodo de la jerarquia con una sola instancia.
- **`MultiClassHandler`** — nodo que admite multiples instancias (colecciones).
- **`ClassMapper`** — construye el arbol de instancias a partir de
  `class_reference` + `class_mapping` + `class_properties`.
- **`ServiceExecuter`** — recibe la peticion de servicio (JSON/ dict) y
  ejecuta los metodos declarados (`SYSServiceMethod`) sobre cada nodo.

El flujo declarativo es:

```
service_metadata (JSON)
        |
        v
ClassMapper  -----> arbol de instancias Product -> Stock
                                    \-> Notification
        |
        v
ServiceExecuter.execute()
        |
        v
ServiceMapper._map()  -> set_properties() -> getattr(inst, SYSServiceMethod)()
```

Cada nodo expone `SYSServiceMethod` y el framework lo invoca por reflexion,
de modo que la logica de negocio vive en las clases `Product`, `Stock`,
`Notification`, no en el framework.

---

## 2. Integraciones implementadas

Esta practica integra **tres fuentes/sistemas** a traves del bus:

### 2.1 Catalogo XLSX (fuente de datos)

- Archivo: `catalogo.xlsx` (generado a partir de `catalogo.csv` si no existe).
- Lector: `catalogo.py` usando `openpyxl`.
- Cada fila del catalogo se convierte en un payload de servicio con la
  jerarquia `Product -> {Stock, Notification}`.

### 2.2 PostgreSQL (persistencia)

- DDL: `init_db.sql` (tablas `products` y `stock` con FK).
- Conexion: `db.py` intenta `psycopg2.connect()` usando la variable de
  entorno `PG_DSN`. Si PostgreSQL no esta disponible, cae automaticamente
  a **SQLite en memoria** para que la demo sea ejecutable sin
  infraestructura.

### 2.3 Mensajeria asincrona

- Implementacion: `messaging.py` con `threading.Thread` + `queue.Queue`.
- Un hilo consumidor dedica a drenar la cola y entregara cada mensaje a
  los handlers suscritos.
- Cada metodo de servicio publica un evento
  (`product.inserted`, `notification`).
- En produccion, basta reemplazar `AsyncBroker` por un cliente
  RabbitMQ/Kafka/Redis Streams; el contrato (`.publish(msg)` y
  `.subscribe(handler)`) se mantiene.

---

## 3. Diagrama de arquitectura

```
        +-----------------------+
        |  catalogo.xlsx / .csv |  (fuente de datos)
        +-----------+-----------+
                    |
                    v
        +-----------------------+        +-------------------------+
        |   catalogo.py         | -----> | service_metadata (JSON) |
        |   (openpyxl reader)   |        +-----------+-------------+
        +-----------------------+                    |
                                                   v
   +---------------------------------------+   +-------------------------------+
   |           microesb framework         |<--| ClassMapper / ServiceExecuter |
   |  (ClassMapper, ClassHandler,         |   +-------------------------------+
   |   ServiceMapper, JSONTransformer)    |
   +-----+-------------+-------------+----+
         |             |             |
         v             v             v
   +-----------+ +-----------+ +----------------+
   | Product   | | Stock     | | Notification   |   <-- clases de servicio
   | .insert() | | .insert() | | .send()        |       (service_implementation.py)
   +-----+-----+ +-----+-----+ +--------+-------+
         |             |                |
         v             v                v
   +---------------------------------------+
   |          db.py (DBWrapper)            |   <-- capa de persistencia
   +-------+--------------------+----------+
           |                    |
           v                    v
   +---------------+    +----------------+
   |  PostgreSQL   |    | SQLite (mock)  |
   | (psycopg2)    |    | (fallback)     |
   +---------------+    +----------------+

                +---------------------------+
                | messaging.py (AsyncBroker)|   <-- bus asincrono
                |  thread + queue.Queue     |
                +-----+----------------+----+
                      |                |
        publish() <---+                +---> consume() -> handlers
                      ^
                      |
              (publicado por Product.insert y Notification.send)

                      En produccion: reemplazar por
                      RabbitMQ / Kafka / Redis Streams
```

**Flujo end-to-end:**

1. El catalogo XLSX se lee y se transforma en un payload JSON.
2. El framework `microesb` mapea el payload a instancias
   `Product -> Stock` / `Notification`.
3. `ServiceExecuter` invoca los metodos declarados (`insert`, `send`).
4. Cada metodo escribe en PostgreSQL (o SQLite) y publica un evento en el
   broker asincrono.
5. El consumidor del broker procesa los eventos sin bloquear al productor
   (mediacion verdaderamente asincrona).

---

## 4. Conclusiones

1. **Desacoplamiento real.** El consumidor del servicio (el script `main`)
   no conoce los backends: solo carga el catalogo y lo entrega al bus.
   Cambiar PostgreSQL por MongoDB, o el broker interno por RabbitMQ, no
   toca el codigo del cliente.

2. **Modelado declarativo productivo.** Definir `class_reference`,
   `class_mapping` y `service_properties` como diccionarios permite
   agregar nodos (p. ej. `Audit`) sin tocar el nucleo del framework; solo
   hay que anadir la clase con `SYSServiceMethod`.

3. **Limitacion clara.** `microesb` es un ESB *in-process*: el bus vive en
   el mismo proceso Python. No reemplaza un broker de mensajeria real ni
   ofrece transporte entre procesos. Su rol aqui es **mediacion y
   transformacion** declarativa, mientras que la mensajeria cruzada entre
   servicios la aporta el componente asincrono que anadimos.

4. **Patron pub/sub.** Al separar la llamada al servicio (`Product.insert`)
   de la notificacion (`AsyncBroker.publish`), el sistema implementa el
   patron *publish-subscribe*: los servicios reaccionan a eventos sin
   acoplarse entre si. Este es el corazon de una arquitectura orientada a
   eventos (EDA) soportada por un ESB.

5. **Trazabilidad.** El `JSONTransformer` del framework permite serializar
   toda la jerarquia de servicios en un solo documento JSON, util para
   auditar el estado de la peticion completa.

6. **Escalabilidad.** Aunque la implementacion de referencia es monolítica,
   el mapeo clase-a-servicio permite mover cada nodo (`Stock`,
   `Notification`) a un microservicio independiente sin cambiar la
   semantica del bus, cumpliendo el principio de *Platform as a Service /
   Microservices* mencionado por el autor del framework.

---

## 5. Como ejecutarlo (resumen ejecutivo)

Ver `README.md` para el procedimiento completo y comandos detallados.
Comando minimo:

```bash
pip install -r requirements.txt
python main.py
```
