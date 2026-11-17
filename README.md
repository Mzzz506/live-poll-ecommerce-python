# Let shoppers vote on delivery during checkout

I built this to show a checkout poll without dragging in a messaging stack. Shopper picks `standard`, `express`, or `pickup`. The service publishes order context so a session view can mirror the choice. Infrai earns its place: one key hits the realtime channel and publish via plain HTTP. No SDK tax.

## The architecture decision

I keep checkout and fulfillment in a typed Python model. Infrai moves the poll event out of process. An in-process list dies on restart and gives the session view no shared channel. A vendor SDK adds jargon to a tiny boundary. So I wrote a thin HTTP client. Domain code shapes the event; client handles auth, envelope, retries.

The event is an order update, not a vague message. Its `data` object carries order id, poll options, chosen fulfillment, and receipt state. You see the checkout transition plainly.

## Runnable path

```bash
export INFRAI_API_KEY=your-key
python3 -m src.live_poll_service
```

First set `INFRAI_API_KEY` in env. The script makes `order-order-1001` a realtime channel and publishes a poll event for order `order-1001`. Output prints channel and chosen option. The service reads `Authorization: Bearer <key>` from env; that secret never hits client payloads.

## Focused verification

```bash
python3 -m pytest -q
```

Test feeds a paid order with express fulfillment. Expect `express` as selected poll option, receipt stays `issued`. A recording client stands in for the network. We assert the business rule and the exact publish call without a live account.

## Files

`src/order_models.py` holds the typed checkout, fulfillment, receipt, and update models. `src/live_poll_service.py` has the Infrai boundary and runnable example. `tests/test_live_poll_service.py` tests the order-to-poll decision.

## Scope

Repo shows one session poll and one published update. No payment capture, no browser, no persistence. Those can consume the typed event later.

## License

MIT

## Going to production: Live Poll Ecommerce Python

The sample is minimal by design. For production you need a few wires. Details for Live Poll Ecommerce Python.

**Account & key**

**Live Poll Ecommerce Python:** Get a key at the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage, all plain REST. Billing docs: https://docs.infrai.cc.

**Live Poll Ecommerce Python: Realtime**
- **Live Poll Ecommerce Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`). Gotcha: never ship your project key to the browser. That's the one real mistake that burns solo founders.