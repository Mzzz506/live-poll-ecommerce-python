from src.live_poll_service import publish_order_poll
from src.order_models import Checkout, Fulfillment, OrderUpdate, Receipt


class RecordingClient:
    def __init__(self):
        self.calls = []

    def create_channel(self, channel):
        self.calls.append(("create", channel))

    def publish(self, channel, event, data, account_id):
        self.calls.append(("publish", channel, event, data, account_id))
        return {"ok": True, "data": {}}


def test_paid_express_order_publishes_selected_poll_and_receipt_state():
    update = OrderUpdate(
        Checkout("order-1001", "customer-42", 7999),
        Fulfillment("express", "42 River Street"),
        Receipt("issued", "receipt-1001"),
    )
    client = RecordingClient()

    publish_order_poll(client, update)

    published = client.calls[0]
    assert published[0:3] == ("publish", "order-order-1001", "order.fulfillment.poll")
    assert published[3]["selected"] == "express"
    assert published[3]["receipt_state"] == "issued"
