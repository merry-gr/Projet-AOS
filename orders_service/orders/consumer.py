import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print("🔔 New order received from RabbitMQ:")
    print(data)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='orders')  # ✅ SAME NAME

channel.basic_consume(
    queue='orders',  # ✅ SAME NAME
    on_message_callback=callback,
    auto_ack=True
)

print("🟢 Waiting for messages...")
channel.start_consuming()