from dataclasses import dataclass, field


@dataclass
class MarketConfig:
    name: str
    base_currency: str
    asset_name: str
    initial_price: float
    price_std: float = 10.0
    book_volume: int = 1000
    rf: float = 5e-4
    transaction_cost: float = 0.0
    position: tuple[int, int] = (0, 0)


@dataclass
class FXConfig:
    name: str = "FX"
    base_currency: str = "CUR_A"
    quote_currency: str = "CUR_B"
    initial_rate: float = 1.0
    price_std: float = 0.05
    book_volume: int = 500
    transaction_cost: float = 0.0
    position: tuple[int, int] = (5, 5)


@dataclass
class ShockConfig:
    market_name: str
    iteration: int
    delta_price: float
    spillover_beta: float = 0.0


@dataclass
class AgentSetup:
    n_a_only_random: int = 0
    n_b_only_random: int = 0
    n_cross_random: int = 0
    n_a_only_fundamental: int = 0
    n_b_only_fundamental: int = 0
    n_cross_fundamental: int = 0
    n_fx_traders: int = 0


@dataclass
class SimulationConfig:
    grid_size: tuple[int, int] = (20, 20)
    tau: float = 0.0
    steps: int = 500
    seed: int = 42
    markets: list = field(default_factory=list)
    fx_market: FXConfig | None = None
    shocks: list = field(default_factory=list)
    agent_setup: AgentSetup = field(default_factory=AgentSetup)