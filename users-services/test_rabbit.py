import pika
import time

while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq')
        )
        break
    except:
        print("Waiting for RabbitMQ...")
        time.sleep(3)

channel = connection.channel()
channel.queue_declare(queue='test_queue')

channel.basic_publish(
    exchange='',
    routing_key='test_queue',
    body='Hello'
)

print("Message sent")
connection.close()