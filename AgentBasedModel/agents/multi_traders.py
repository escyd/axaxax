import random
from types import SimpleNamespace

from AgentBasedModel.utils import Order
from AgentBasedModel.utils.spatial import transport_cost


class MultiTrader:
    id = 0

    def __init__(
        self,
        name: str,
        markets: dict,
        fx_market=None,
        cash_a: float = 0.0,
        cash_b: float = 0.0,
        assets: int = 0,
        position: tuple[int, int] = (0, 0),
        access_mode: str = "A_ONLY",
        home_currency: str = "CUR_A",
    ):
        self.name = name
        self.id = MultiTrader.id
        MultiTrader.id += 1

        self.type = "Unknown"
        self.markets = markets
        self.fx_market = fx_market

        self.cash = {
            "CUR_A": float(cash_a),
            "CUR_B": float(cash_b),
        }
        self.assets = assets
        self.orders = []
        self.position = position
        self.access_mode = access_mode
        self.home_currency = home_currency

    def make_order_proxy(self, currency: str):
        return SimpleNamespace(
            cash=float(self.cash[currency]),
            assets=int(self.assets),
            orders=[]
        )

    def available_markets(self):
        if self.access_mode == "A_ONLY":
            return ["A"]
        if self.access_mode == "B_ONLY":
            return ["B"]
        if self.access_mode == "CROSS":
            return ["A", "B"]
        if self.access_mode == "FX_ONLY":
            return []
        return []

    def distance_cost(self, market_name: str, tau: float) -> float:
        market = self.markets[market_name]
        return transport_cost(self.position, market.position, tau)

    def effective_buy_price(self, market_name: str, tau: float) -> float:
        market = self.markets[market_name]
        spread = market.spread()
        if spread is None:
            return float("inf")

        ask = spread["ask"] * (1 + market.transaction_cost)
        total = ask + self.distance_cost(market_name, tau)

        if market.base_currency != self.home_currency and self.fx_market is not None:
            fx_rate = self.fx_market.price()
            if market.base_currency == "CUR_B" and self.home_currency == "CUR_A":
                total *= fx_rate
            elif market.base_currency == "CUR_A" and self.home_currency == "CUR_B":
                total /= max(fx_rate, 1e-9)

        return total

    def effective_sell_price(self, market_name: str, tau: float) -> float:
        market = self.markets[market_name]
        spread = market.spread()
        if spread is None:
            return 0.0

        bid = spread["bid"] * (1 - market.transaction_cost)
        total = bid - self.distance_cost(market_name, tau)

        if market.base_currency != self.home_currency and self.fx_market is not None:
            fx_rate = self.fx_market.price()
            if market.base_currency == "CUR_B" and self.home_currency == "CUR_A":
                total *= fx_rate
            elif market.base_currency == "CUR_A" and self.home_currency == "CUR_B":
                total /= max(fx_rate, 1e-9)

        return total

    def choose_best_market_to_buy(self, tau: float):
        candidates = self.available_markets()
        if not candidates:
            return None
        scored = [(m, self.effective_buy_price(m, tau)) for m in candidates]
        scored.sort(key=lambda x: x[1])
        return scored[0][0]

    def choose_best_market_to_sell(self, tau: float):
        candidates = self.available_markets()
        if not candidates:
            return None
        scored = [(m, self.effective_sell_price(m, tau)) for m in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]

    def ensure_currency(self, currency: str, amount_needed: float):
        if self.cash[currency] >= amount_needed:
            return True

        if self.fx_market is None:
            return False

        if currency == "CUR_B" and self.cash["CUR_A"] > 0:
            need = amount_needed - self.cash["CUR_B"]
            rate = self.fx_market.price()
            amount_a = need / max(rate, 1e-9)
            amount_a = min(amount_a, self.cash["CUR_A"])
            converted = self.fx_market.convert(amount_a, "CUR_A", "CUR_B")
            self.cash["CUR_A"] -= amount_a
            self.cash["CUR_B"] += converted
            return self.cash["CUR_B"] >= amount_needed

        if currency == "CUR_A" and self.cash["CUR_B"] > 0:
            need = amount_needed - self.cash["CUR_A"]
            rate = self.fx_market.price()
            amount_b = need * rate
            amount_b = min(amount_b, self.cash["CUR_B"])
            converted = self.fx_market.convert(amount_b, "CUR_B", "CUR_A")
            self.cash["CUR_B"] -= amount_b
            self.cash["CUR_A"] += converted
            return self.cash["CUR_A"] >= amount_needed

        return False


class RandomMultiTrader(MultiTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "Random"

    def call(self, tau: float = 0.0):
        side = "buy" if random.random() > 0.5 else "sell"
        qty = random.randint(1, 3)

        if side == "buy":
            market_name = self.choose_best_market_to_buy(tau)
            if market_name is None:
                return

            market = self.markets[market_name]
            spread = market.spread()
            if spread is None:
                return

            ask = spread["ask"]
            currency = market.base_currency
            total_cost = ask * qty

            if not self.ensure_currency(currency, total_cost):
                return

            proxy = self.make_order_proxy(currency)
            order = Order(ask, qty, "bid", proxy)
            market.market_order(order)

            self.cash[currency] -= total_cost
            self.assets += qty

        else:
            if self.assets < qty:
                return

            market_name = self.choose_best_market_to_sell(tau)
            if market_name is None:
                return

            market = self.markets[market_name]
            spread = market.spread()
            if spread is None:
                return

            bid = spread["bid"]
            currency = market.base_currency

            proxy = self.make_order_proxy(currency)
            order = Order(bid, qty, "ask", proxy)
            market.market_order(order)

            self.assets -= qty
            self.cash[currency] += bid * qty


class FundamentalistMultiTrader(MultiTrader):
    def __init__(self, *args, fundamental_price: float = 100.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "Fundamentalist"
        self.fundamental_price = fundamental_price

    def call(self, tau: float = 0.0):
        buy_market = self.choose_best_market_to_buy(tau)
        sell_market = self.choose_best_market_to_sell(tau)

        if buy_market is None or sell_market is None:
            return

        buy_effective = self.effective_buy_price(buy_market, tau)
        sell_effective = self.effective_sell_price(sell_market, tau)

        qty = 1

        if self.fundamental_price > buy_effective:
            market = self.markets[buy_market]
            spread = market.spread()
            if spread is None:
                return

            ask = spread["ask"]
            currency = market.base_currency
            total_cost = ask * qty

            if not self.ensure_currency(currency, total_cost):
                return

            proxy = self.make_order_proxy(currency)
            order = Order(ask, qty, "bid", proxy)
            market.market_order(order)

            self.cash[currency] -= total_cost
            self.assets += qty

        elif self.fundamental_price < sell_effective and self.assets >= qty:
            market = self.markets[sell_market]
            spread = market.spread()
            if spread is None:
                return

            bid = spread["bid"]
            currency = market.base_currency

            proxy = self.make_order_proxy(currency)
            order = Order(bid, qty, "ask", proxy)
            market.market_order(order)

            self.assets -= qty
            self.cash[currency] += bid * qty


class FXTrader(MultiTrader):
    def __init__(self, *args, **kwargs):
        kwargs["access_mode"] = "FX_ONLY"
        super().__init__(*args, **kwargs)
        self.type = "FXTrader"

    def call(self, tau: float = 0.0):
        if self.fx_market is None:
            return

        amount = random.uniform(1, 20)

        if random.random() > 0.5 and self.cash["CUR_A"] >= amount:
            converted = self.fx_market.convert(amount, "CUR_A", "CUR_B")
            self.cash["CUR_A"] -= amount
            self.cash["CUR_B"] += converted
        elif self.cash["CUR_B"] >= amount:
            converted = self.fx_market.convert(amount, "CUR_B", "CUR_A")
            self.cash["CUR_B"] -= amount
            self.cash["CUR_A"] += converted