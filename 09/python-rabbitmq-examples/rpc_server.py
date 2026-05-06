import pika
import time

def on_request(ch, method, props, body):
    payload = body.decode('utf-8')
    print(f" [.] Received request with payload: {payload}")
    
    # Simulate some work
    time.sleep(2)
    response = f"Processed: {payload}"
    
    print(f" [x] Sending response: {response}")
    
    # Implement callback: sending the response back to the client's reply_to queue
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id,
        ),
        body=str(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

import os

rabbitmq_host = os.environ.get('RABBITMQ_HOST', '127.0.0.1')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
