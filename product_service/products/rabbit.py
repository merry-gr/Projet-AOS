import json
import os
from typing import Any

def _amqp_url() -> str:
    # Docker compose service name is "rabbitmq"
    return os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")


def publish_event(event_type: str, payload: dict[str, Any]) -> None:
    """
    Publish a JSON event to the 'medconnect.events' exchange.
    Safe to call in web requests: failures won't crash the request.
    """
    try:
        import pika

        params = pika.URLParameters(_amqp_url())
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange="medconnect.events", exchange_type="topic", durable=True)

        body = json.dumps({"type": event_type, "payload": payload}).encode("utf-8")
        channel.basic_publish(
            exchange="medconnect.events",
            routing_key=event_type,
            body=body,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        connection.close()
    except Exception:
        # Don't break the API if RabbitMQ is down.
        return

