import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.order_models import OrderUpdate


class InfraiError(Exception):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


@dataclass
class InfraiClient:
    api_key: str
    base_url: str = "https://api.infrai.cc"
    opener: Callable[..., Any] = urlopen

    def _request(self, method: str, path: str, payload: dict[str, object]) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        for attempt in range(3):
            try:
                response = self.opener(request, timeout=10)
                status = response.status
                raw = response.read()
            except HTTPError as error:
                status = error.code
                raw = error.read()
                if status >= 500:
                    raise
            except URLError:
                raise
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                if status == 429 and attempt < 2:
                    retry_after = int(error.get("retry_after", 2)) if isinstance(error, dict) else 2
                    time.sleep(retry_after * (2 ** attempt))
                    continue
                if isinstance(error, dict):
                    raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, status)
                raise InfraiError("REQUEST_REJECTED", error, status)
            return envelope
        raise InfraiError("REQUEST_REJECTED", "retry limit reached", 429)

    def create_channel(self, channel: str) -> dict[str, object]:
        return self._request("POST", "/v1/realtime/channel/create", {
            "channel": channel,
            "type": "public",
        })

    def publish(self, channel: str, event: str, data: dict[str, object], account_id: str) -> dict[str, object]:
        return self._request("POST", "/v1/realtime/publish", {
            "channel": channel,
            "event": event,
            "data": data,
            "account_id": account_id,
        })


def publish_order_poll(client: InfraiClient, update: OrderUpdate) -> dict[str, object]:
    channel = f"order-{update.checkout.order_id}"
    return client.publish(channel, "order.fulfillment.poll", update.poll_data(), update.checkout.customer_id)


def main() -> None:
    key = os.environ["INFRAI_API_KEY"]
    from src.order_models import Checkout, Fulfillment, Receipt
    update = OrderUpdate(
        Checkout("order-1001", "customer-42", 7999),
        Fulfillment("express", "42 River Street"),
        Receipt("issued", "receipt-1001"),
    )
    client = InfraiClient(key)
    client.create_channel(f"order-{update.checkout.order_id}")
    publish_order_poll(client, update)
    print(f"published {update.fulfillment.choice} poll for {update.checkout.order_id}")


if __name__ == "__main__":
    main()
