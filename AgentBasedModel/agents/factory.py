import random

from AgentBasedModel.agents.multi_traders import (
    RandomMultiTrader,
    FundamentalistMultiTrader,
    FXTrader,
)


def random_position(grid_size: tuple[int, int]) -> tuple[int, int]:
    return (
        random.randint(0, grid_size[0] - 1),
        random.randint(0, grid_size[1] - 1),
    )


def build_multi_traders(
    markets: dict,
    fx_market,
    grid_size: tuple[int, int],
    n_a_only_random: int = 0,
    n_b_only_random: int = 0,
    n_cross_random: int = 0,
    n_a_only_fundamental: int = 0,
    n_b_only_fundamental: int = 0,
    n_cross_fundamental: int = 0,
    n_fx_traders: int = 0,
):
    traders = []

    for i in range(n_a_only_random):
        traders.append(
            RandomMultiTrader(
                name=f"AOnlyRandom_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=1000,
                cash_b=0,
                assets=5,
                position=random_position(grid_size),
                access_mode="A_ONLY",
                home_currency="CUR_A",
            )
        )

    for i in range(n_b_only_random):
        traders.append(
            RandomMultiTrader(
                name=f"BOnlyRandom_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=0,
                cash_b=1000,
                assets=5,
                position=random_position(grid_size),
                access_mode="B_ONLY",
                home_currency="CUR_B",
            )
        )

    for i in range(n_cross_random):
        traders.append(
            RandomMultiTrader(
                name=f"CrossRandom_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=500,
                cash_b=500,
                assets=5,
                position=random_position(grid_size),
                access_mode="CROSS",
                home_currency="CUR_A",
            )
        )

    for i in range(n_a_only_fundamental):
        traders.append(
            FundamentalistMultiTrader(
                name=f"AOnlyFund_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=1000,
                cash_b=0,
                assets=5,
                position=random_position(grid_size),
                access_mode="A_ONLY",
                home_currency="CUR_A",
                fundamental_price=100.0,
            )
        )

    for i in range(n_b_only_fundamental):
        traders.append(
            FundamentalistMultiTrader(
                name=f"BOnlyFund_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=0,
                cash_b=1000,
                assets=5,
                position=random_position(grid_size),
                access_mode="B_ONLY",
                home_currency="CUR_B",
                fundamental_price=100.0,
            )
        )

    for i in range(n_cross_fundamental):
        traders.append(
            FundamentalistMultiTrader(
                name=f"CrossFund_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=500,
                cash_b=500,
                assets=5,
                position=random_position(grid_size),
                access_mode="CROSS",
                home_currency="CUR_A",
                fundamental_price=100.0,
            )
        )

    for i in range(n_fx_traders):
        traders.append(
            FXTrader(
                name=f"FXTrader_{i}",
                markets=markets,
                fx_market=fx_market,
                cash_a=1000,
                cash_b=1000,
                assets=0,
                position=random_position(grid_size),
                home_currency="CUR_A",
            )
        )

    return traders