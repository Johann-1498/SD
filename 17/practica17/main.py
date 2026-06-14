"""
ESB demo (practica 17) — main entry point.

Wires three integrations through the microesb framework:
  1. Catalog reader (CSV / XLSX input source)
  2. PostgreSQL persistence (SQLite fallback when PG unavailable)
  3. Async messaging broker (thread + queue)

Run:
    python main.py
"""
import logging
import os
import sys

from microesb import microesb

from class_reference import class_reference
from class_mapping import class_mapping
from service_properties import service_properties
from catalogo import read_catalog, OPENPYXL_AVAILABLE
from db import DBWrapper
from messaging import AsyncBroker, default_handler, wait_for_drain


HERE = os.path.dirname(os.path.abspath(__file__))


def build_xlsx_if_needed():
    """Generate catalogo.xlsx from catalogo.csv when openpyxl is available."""
    xlsx_path = os.path.join(HERE, 'catalogo.xlsx')
    csv_path = os.path.join(HERE, 'catalogo.csv')
    if os.path.exists(xlsx_path):
        return xlsx_path
    if not OPENPYXL_AVAILABLE:
        return csv_path
    from openpyxl import Workbook
    import csv as _csv
    wb = Workbook()
    ws = wb.active
    ws.title = 'catalog'
    with open(csv_path, newline='', encoding='utf-8') as fh:
        for row in _csv.reader(fh):
            ws.append(row)
    wb.save(xlsx_path)
    print(f'[SETUP] Generated {xlsx_path} from CSV')
    return xlsx_path


def build_service_data(records):
    """Convert raw catalog records into microesb service_metadata payload."""
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


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    print('=' * 70)
    print(' Practica 17 — Python Micro-ESB Demo')
    print(' Integraciones: Catalogo XLS + PostgreSQL + Mensajeria Asincrona')
    print('=' * 70)

    # 1) Start async broker
    broker = AsyncBroker(name='esb-broker')
    broker.subscribe(default_handler)
    broker.start()

    # 2) Open DB (PG if available, else in-memory SQLite)
    pg_dsn = os.environ.get('PG_DSN')  # e.g. "dbname='esb' user='postgres' host='localhost' password='secret'"
    db = DBWrapper(dsn=pg_dsn)
    print(f'[DB] backend={db.backend}')

    # 3) Read catalog
    catalog_path = build_xlsx_if_needed()
    records = read_catalog(catalog_path)
    print(f'[CATALOG] {len(records)} registros leidos desde {os.path.basename(catalog_path)}')

    # 4) Build class mapper once
    class_mapper = microesb.ClassMapper(
        class_references=class_reference,
        class_mappings=class_mapping,
        class_properties=service_properties,
    )

    # 5) Build service payload and inject dbcon + mq references at root
    service_data = build_service_data(records)
    for item in service_data['data']:
        item['Product']['dbcon'] = db
        item['Product']['mq'] = broker

    # 6) Execute through ESB
    print('[ESB] ejecutando servicio...')
    results = microesb.ServiceExecuter().execute(
        class_mapper=class_mapper,
        service_data=service_data,
    )
    print(f'[ESB] {len(results)} llamadas de servicio completadas')

    # 7) Wait for async drain
    wait_for_drain(broker, timeout=5.0)

    # 8) Print final state
    print('\n--- Estado final DB ---')
    if db.backend == 'postgres':
        cur = db.execute('SELECT sku, name, price FROM products ORDER BY sku')
    else:
        cur = db.execute('SELECT sku, name, price FROM products ORDER BY sku')
    for row in cur.fetchall():
        print(' ', dict(row) if not isinstance(row, dict) else row)

    cur = db.execute('SELECT sku, warehouse, quantity FROM stock ORDER BY sku, warehouse')
    print('--- Stock por almacen ---')
    for row in cur.fetchall():
        print(' ', dict(row) if not isinstance(row, dict) else row)

    # 9) Optional: dump hierarchical JSON
    print('\n--- Jerarquia JSON (primer item) ---')
    try:
        hierarchy = microesb.ServiceExecuter().execute_get_hierarchy(
            class_mapper=microesb.ClassMapper(
                class_references=class_reference,
                class_mappings=class_mapping,
                class_properties=service_properties,
            ),
            service_data={'data': [service_data['data'][0]]},
        )
        import json
        print(json.dumps(hierarchy, indent=2, default=str)[:800])
    except Exception as exc:
        print(f'(hierarchy dump skipped: {exc})')

    # 10) Shutdown
    broker.stop()
    db.close()
    print('\n[OK] Demo completado.')


if __name__ == '__main__':
    sys.exit(main() or 0)
