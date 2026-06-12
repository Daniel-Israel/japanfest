from os import getenv

import pika


def connect_to_queue():

    global channel

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=getenv("QUEUE_HOST", "localhost"),
            credentials=pika.PlainCredentials(
                username=getenv("QUEUE_USER", "admin"),
                password=getenv("QUEUE_PASS", "rabbitmqpassword")
            )
        )
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange=getenv("QUEUE_NAME", "receipts"),
        exchange_type="direct",
        durable=True
    )

    return channel
