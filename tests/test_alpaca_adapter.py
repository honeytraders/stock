import pytest
import respx
from httpx import Response

from broker_adapters.alpaca import AlpacaAdapter, AlpacaConfig
from core_contracts.models import OrderType, Side


@pytest.fixture
def alpaca_client():
    config = AlpacaConfig(api_key="test_key", secret_key="test_secret")
    return AlpacaAdapter(config)


@respx.mock
def test_get_account(alpaca_client):
    route = respx.get("https://paper-api.alpaca.markets/v2/account").mock(
        return_value=Response(200, json={"id": "acc_1", "status": "ACTIVE", "equity": "100000"})
    )
    account = alpaca_client.get_account_status()
    assert account["id"] == "acc_1"
    assert route.called


@respx.mock
def test_submit_order(alpaca_client):
    respx.post("https://paper-api.alpaca.markets/v2/orders").mock(
        return_value=Response(
            201,
            json={
                "id": "ord_1",
                "client_order_id": "test_cid",
                "symbol": "AAPL",
                "qty": "10",
                "side": "buy",
                "type": "market",
            },
        )
    )
    order = alpaca_client.submit_order("AAPL", 10, Side.BUY, OrderType.MARKET, "test_cid")
    assert order.id == "ord_1"
    assert order.symbol == "AAPL"
    assert order.quantity == 10
