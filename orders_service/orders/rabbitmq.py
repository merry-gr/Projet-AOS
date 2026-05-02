import pika
import json

def send_order_created_message(order):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
        )
        channel = connection.channel()

        channel.queue_declare(queue='order_created')

        items_data = []
        for item in order.items.all():
            items_data.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "vendor": item.product.vendor.username
            })

        message = {
            "order_id": order.id,
            "buyer": order.buyer.username,
            "status": order.status,
            "items": items_data
        }

        channel.basic_publish(
            exchange='',
            routing_key='order_created',
            body=json.dumps(message)
        )

        print("Message sent to RabbitMQ:", message)
        connection.close()

    except Exception as e:
        print("RabbitMQ error:", e)