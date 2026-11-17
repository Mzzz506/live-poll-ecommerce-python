from dataclasses import dataclass
from typing import Literal


FulfillmentChoice = Literal["standard", "express", "pickup"]
ReceiptState = Literal["pending", "issued"]


@dataclass(frozen=True)
class Checkout:
    order_id: str
    customer_id: str
    total_cents: int


@dataclass(frozen=True)
class Fulfillment:
    choice: FulfillmentChoice
    address: str


@dataclass(frozen=True)
class Receipt:
    state: ReceiptState
    number: str


@dataclass(frozen=True)
class OrderUpdate:
    checkout: Checkout
    fulfillment: Fulfillment
    receipt: Receipt

    def poll_data(self) -> dict[str, object]:
        return {
            "order_id": self.checkout.order_id,
            "customer_id": self.checkout.customer_id,
            "total_cents": self.checkout.total_cents,
            "options": ["standard", "express", "pickup"],
            "selected": self.fulfillment.choice,
            "receipt_state": self.receipt.state,
        }
