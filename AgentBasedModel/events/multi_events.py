class MultiMarketPriceShock:
    def __init__(self, market_name: str, iteration: int, delta_price: float, spillover_beta: float = 0.0):
        self.market_name = market_name
        self.iteration = iteration
        self.delta_price = delta_price
        self.spillover_beta = spillover_beta

    def __repr__(self):
        return (
            f"MultiMarketPriceShock(market={self.market_name}, "
            f"it={self.iteration}, dp={self.delta_price}, beta={self.spillover_beta})"
        )

    def apply(self, simulator):
        target_market = simulator.markets[self.market_name]
        target_market.apply_price_shock(self.delta_price)

        for name, market in simulator.markets.items():
            if name != self.market_name:
                market.apply_price_shock(self.delta_price * self.spillover_beta)