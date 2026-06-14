"""
Flask web app - visual demo for ESB practica 17.

Endpoints:
  GET  /            -> dashboard (HTML)
  POST /run         -> ejecuta pipeline ESB
  GET  /events      -> SSE stream of broker events + log lines
  GET  /state       -> JSON con tablas products/stock + queue length
  POST /reset       -> limpia DB + log (SQLite fallback only)
"""
import json
import logging
import os
import queue
import sys
import threading
import time

from flask import Flask, Response, render_template, jsonify, request

from class_reference import class_reference
from class_mapping import class_mapping
from service_properties import service_properties
from catalogo import read_catalog
from db import DBWrapper
from messaging import AsyncBroker, wait_for_drain

from microesb import microesb

HERE = os.path.dirname(os.path.abspath(__file__))


class UIHandler(logging.Handler):
    """Captura registros de logging y los empuja al event_bus."""
    def emit(self, record):
        try:
            EVENT_BUS.put_nowait({
                'type': 'log',
                'level': record.levelname,
                'name': record.name,
                'msg': record.getMessage(),
                'ts': time.time(),
            })
        except queue.Full:
            pass


EVENT_BUS = queue.Queue(maxsize=1000)


class UIBroker(AsyncBroker):
    """AsyncBroker que tambien publica en EVENT_BUS para SSE."""
    def publish(self, message):
        super().publish(message)
        try:
            EVENT_BUS.put_nowait({
                'type': 'broker',
                'msg': message,
                'ts': time.time(),
            })
        except queue.Full:
            pass


def ui_handler_default(message):
    """Handler del broker para la UI: solo registra en consola."""
    payload = message if isinstance(message, str) else json.dumps(message)
    print(f'[BROKER] {payload}')


app = Flask(__name__)

# Estado global compartido
STATE = {
    'db': None,
    'broker': None,
    'lock': threading.Lock(),
    'running': False,
    'last_run': None,
}


def init_state():
    if STATE['db'] is None:
        STATE['db'] = DBWrapper(dsn=os.environ.get('PG_DSN'))
    if STATE['broker'] is None:
        broker = UIBroker(name='ui-broker')
        broker.subscribe(ui_handler_default)
        broker.start()
        STATE['broker'] = broker


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h, UIHandler) for h in root.handlers):
        root.addHandler(UIHandler())


def build_service_data(records):
    data = []
    for rec in records:
        item = {
            'Product': {
                'SYSServiceMethod': 'insert',
                'sku': rec['sku'],
                'name': rec['name'],
                'price': float(rec['price']),
                'Stock': {
                    'SYSServiceMethod': 'insert',
                    'warehouse': rec['warehouse'],
                    'quantity': int(rec['quantity']),
                },
                'Notification': {
                    'SYSServiceMethod': 'send',
                    'channel': rec.get('channel', 'email'),
                    'message': rec.get('message', ''),
                },
            }
        }
        data.append(item)
    return {'data': data}


def run_pipeline():
    """Ejecuta todo el flujo ESB y devuelve resumen."""
    init_state()
    db = STATE['db']
    broker = STATE['broker']
    records = read_catalog(os.path.join(HERE, 'catalogo.xlsx'))
    if not os.path.exists(os.path.join(HERE, 'catalogo.xlsx')):
        records = read_catalog(os.path.join(HERE, 'catalogo.csv'))

    class_mapper = microesb.ClassMapper(
        class_references=class_reference,
        class_mappings=class_mapping,
        class_properties=service_properties,
    )
    service_data = build_service_data(records)
    for item in service_data['data']:
        item['Product']['dbcon'] = db
        item['Product']['mq'] = broker

    started = time.time()
    results = microesb.ServiceExecuter().execute(
        class_mapper=class_mapper,
        service_data=service_data,
    )
    wait_for_drain(broker, timeout=5.0)
    elapsed = time.time() - started
    return {
        'records': len(records),
        'calls': len(results),
        'elapsed_ms': int(elapsed * 1000),
    }


@app.route('/')
def index():
    init_state()
    return render_template('index.html', backend=STATE['db'].backend)


@app.route('/run', methods=['POST'])
def run():
    if STATE['running']:
        return jsonify({'error': 'pipeline en ejecucion'}), 409
    STATE['running'] = True
    try:
        summary = run_pipeline()
        STATE['last_run'] = summary
        return jsonify(summary)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(exc), 'trace': traceback.format_exc()}), 500
    finally:
        STATE['running'] = False


@app.route('/reset', methods=['POST'])
def reset():
    """Solo disponible en SQLite (en PG se mantiene el estado)."""
    init_state()
    db = STATE['db']
    if db.backend != 'sqlite':
        return jsonify({'error': 'reset solo permitido en modo SQLite'}), 400
    db.execute('DELETE FROM products')
    db.execute('DELETE FROM stock')
    db.commit()
    STATE['last_run'] = None
    return jsonify({'ok': True})


@app.route('/state')
def state():
    init_state()
    db = STATE['db']
    products = [dict(r) for r in db.execute(
        'SELECT sku, name, price FROM products ORDER BY sku').fetchall()]
    stock = [dict(r) for r in db.execute(
        'SELECT sku, warehouse, quantity FROM stock ORDER BY sku, warehouse'
    ).fetchall()]
    return jsonify({
        'backend': db.backend,
        'queue_size': STATE['broker']._queue.qsize(),
        'queue_unfinished': STATE['broker']._queue.unfinished_tasks,
        'last_run': STATE['last_run'],
        'running': STATE['running'],
        'products': products,
        'stock': stock,
    })


@app.route('/events')
def events():
    def stream():
        # heartbeat inicial
        yield 'event: hello\ndata: {}\n\n'
        while True:
            try:
                evt = EVENT_BUS.get(timeout=15)
                yield f'data: {json.dumps(evt)}\n\n'
            except queue.Empty:
                yield ': ping\n\n'
    return Response(stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no'})


def main():
    setup_logging()
    logging.getLogger().info('UI ESB demo arrancando')
    init_state()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == '__main__':
    main()
