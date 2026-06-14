"""
Service implementations consumed by microesb framework.
Each class corresponds to a node in the class_reference hierarchy.
"""
import json
import logging

from microesb import microesb

logger = logging.getLogger(__name__)


class Product(microesb.ClassHandler):
    """Product node. Inserts into DB and emits an event to async broker."""

    def __init__(self):
        super().__init__()
        self.dbcon = None
        self.mq = None

    def insert(self):
        logger.info('Product.insert sku=%s name=%s price=%s',
                    self.sku, self.name, self.price)
        self.dbcon.execute(
            'INSERT INTO products (sku, name, price) VALUES (%s, %s, %s)',
            (self.sku, self.name, float(self.price)),
        )
        self.dbcon.commit()
        self.mq.publish({
            'event': 'product.inserted',
            'sku': self.sku,
            'name': self.name,
            'price': float(self.price),
        })


class Stock(microesb.ClassHandler):
    """Stock sub-node. Inserts inventory record linked to product SKU."""

    def __init__(self):
        super().__init__()

    def insert(self):
        parent = self.parent_object
        dbcon = parent.dbcon
        logger.info('Stock.insert sku=%s warehouse=%s qty=%s',
                    parent.sku, self.warehouse, self.quantity)
        dbcon.execute(
            'INSERT INTO stock (sku, warehouse, quantity) VALUES (%s, %s, %s)',
            (parent.sku, self.warehouse, int(self.quantity)),
        )
        dbcon.commit()


class Notification(microesb.ClassHandler):
    """Notification sub-node. Sends a message via async broker."""

    def __init__(self):
        super().__init__()

    def send(self):
        parent = self.parent_object
        mq = parent.mq
        payload = self.message or f'Product {parent.sku} processed'
        logger.info('Notification.send channel=%s message=%s', self.channel, payload)
        mq.publish({
            'event': 'notification',
            'channel': self.channel,
            'sku': parent.sku,
            'message': payload,
        })
