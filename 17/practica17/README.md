# Practica 17 — Python Micro-ESB Demo

Demo runnable del patron ESB (Enterprise Service Bus) usando el framework
`microesb`, con tres integraciones:

1. **Catalogo XLSX** como fuente de datos (`catalogo.py` + `catalogo.xlsx`).
2. **PostgreSQL** como persistencia (`db.py` + `init_db.sql`).
3. **Mensajeria asincrona** con thread + queue (`messaging.py`).

> La teoria, el diagrama de arquitectura y las conclusiones estan en
> **`INFORME.MD`**.

## Requisitos

- Python 3.8+
- Paquetes: `microesb`, `openpyxl`, `psycopg2-binary` (PostgreSQL opcional)

## Instalacion

```bash
# 1. Instalar el framework microesb (incluido en este repositorio)
cd ../python-micro-esb
pip install -e .

# 2. Instalar dependencias de la practica
cd ../practica17
pip install -r requirements.txt
```

## Ejecucion rapida (sin PostgreSQL)

```bash
python main.py
```

La demo usa SQLite en memoria automaticamente si PostgreSQL no esta
disponible. La salida muestra:

- Registros leidos del catalogo.
- Eventos entregados por el broker asincrono.
- Estado final de las tablas `products` y `stock`.
- Jerarquia JSON del primer item procesado.

## Ejecucion con PostgreSQL real

Opcion A — Docker:

```bash
docker run --name pg-esb -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_DB=esb -p 5432:5432 -d postgres:16

# cargar esquema
psql -U postgres -h localhost -f init_db.sql
```

Opcion B — Instalacion local:

```bash
sudo -u postgres psql -c "CREATE DATABASE esb;"
sudo -u postgres psql -d esb -f init_db.sql
```

Luego exportar el DSN y ejecutar:

```bash
# Linux / macOS
export PG_DSN="dbname='esb' user='postgres' host='localhost' password='secret'"
python main.py

# Windows PowerShell
$env:PG_DSN="dbname='esb' user='postgres' host='localhost' password='secret'"
python main.py

# Windows CMD
set PG_DSN=dbname='esb' user='postgres' host='localhost' password='secret'
python main.py
```

El log inicial debera mostrar `[DB] backend=postgres`.

## Estructura

```
practica17/
|-- main.py                     # Entry point
|-- esbconfig.py                # Importa clases de servicio al framework
|-- class_reference.py          # Jerarquia: Product -> {Stock, Notification}
|-- class_mapping.py            # Mapping clase logica -> clase implementacion
|-- service_properties.py       # Propiedades y metodos declarados por nodo
|-- service_implementation.py   # Logica: Product.insert, Stock.insert, Notification.send
|-- catalogo.py                 # Lector XLSX / CSV
|-- catalogo.csv                # Catalogo de entrada (7 registros)
|-- catalogo.xlsx               # Generado automaticamente desde el CSV
|-- db.py                       # Wrapper PostgreSQL + fallback SQLite
|-- messaging.py                # Broker asincrono (thread + queue)
|-- init_db.sql                 # DDL PostgreSQL
|-- requirements.txt
|-- INFORME.MD                  # Teoria, diagrama, conclusiones
`-- README.md                   # Este archivo
```

## Como extender

- **Agregar un nodo** (p. ej. `Audit`): anadir clase en
  `service_implementation.py`, anadir entrada en `class_reference.py`,
  `class_mapping.py`, `service_properties.py` y `esbconfig.py`.
- **Reemplazar el broker** por RabbitMQ: implementar `publish()` con
  `pika` y un consumidor separado en otro proceso.
- **Reemplazar PostgreSQL** por MongoDB: reescribir `db.py` con
  `pymongo`; las clases de servicio no cambian.
