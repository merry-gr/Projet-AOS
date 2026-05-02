import os

import pika
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Consume RabbitMQ events from medconnect.events (for verification/debug)."

    def handle(self, *args, **options):
        amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
        params = pika.URLParameters(amqp_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.exchange_declare(exchange="medconnect.events", exchange_type="topic", durable=True)
        result = channel.queue_declare(queue="orders_service.debug", durable=True)
        queue_name = result.method.queue

        channel.queue_bind(queue=queue_name, exchange="medconnect.events", routing_key="#")

        self.stdout.write(self.style.SUCCESS("Consuming events. Press CTRL+C to stop."))

        def on_message(ch, method, properties, body):
            try:
                text = body.decode("utf-8", errors="replace")
            except Exception:
                text = str(body)
            self.stdout.write(f"[{method.routing_key}] {text}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=50)
        channel.basic_consume(queue=queue_name, on_message_callback=on_message)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write("Stopping consumer...")
        finally:
            try:
                channel.stop_consuming()
            except Exception:
                pass
            connection.close()

