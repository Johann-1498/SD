"""
Async messaging broker (thread + queue based).
No external broker (RabbitMQ/Redis) required for demo.
Drop-in replacement: swap enqueue() with pika/RabbitMQ for production.
"""
import json
import logging
import threading
import queue
import time

logger = logging.getLogger(__name__)


class AsyncBroker:
    """In-process async messaging broker.

    Producer threads call .publish(message). A single consumer thread
    drains the queue and invokes registered handlers.
    """

    def __init__(self, name='broker'):
        self.name = name
        self._queue = queue.Queue()
        self._handlers = []
        self._stop_event = threading.Event()
        self._consumer = threading.Thread(
            target=self._consume,
            name=f'{name}-consumer',
            daemon=True,
        )
        self._started = False

    def subscribe(self, handler):
        self._handlers.append(handler)

    def start(self):
        if self._started:
            return
        self._started = True
        self._consumer.start()
        logger.info('Broker %s started', self.name)

    def publish(self, message):
        self._queue.put(message)

    def stop(self):
        self._stop_event.set()
        if self._consumer.is_alive():
            self._consumer.join(timeout=2.0)

    def _consume(self):
        while not self._stop_event.is_set():
            try:
                message = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                for handler in self._handlers:
                    handler(message)
            except Exception as exc:
                logger.error('Handler error: %s', exc)
            finally:
                self._queue.task_done()


def default_handler(message):
    """Print messages as they arrive."""
    payload = message if isinstance(message, str) else json.dumps(message)
    print(f'[BROKER] delivered: {payload}')


def wait_for_drain(broker, timeout=5.0):
    """Block until broker queue empty (or timeout)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if broker._queue.unfinished_tasks == 0:
            return
        time.sleep(0.05)
