import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print("📥 Received:", data)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq')
)

channel = connection.channel()
channel.queue_declare(queue='orders_queue')

channel.basic_consume(
    queue='orders_queue',
    on_message_callback=callback,
    auto_ack=True
)

print("🚀 Waiting for messages...")
channel.start_consuming()