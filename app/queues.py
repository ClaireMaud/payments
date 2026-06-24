from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue

dlq_exchange = RabbitExchange(
    "payments.dlq",
    type=ExchangeType.FANOUT,
    durable=True,
)

dlq_queue = RabbitQueue(
    "payments.dead",
    durable=True,
)

payments_exchange = RabbitExchange(
    "payments",
    type=ExchangeType.DIRECT,
    durable=True,
)

payments_queue = RabbitQueue(
    "payments.new",
    durable=True,
    arguments={"x-dead-letter-exchange": "payments.dlq"},
)
