import inspect
import json
from pathlib import Path

import pytest
from brownie.utils import color

DEADLINE = 999999999999999
UPDATE_BENCHMARKS = False


def process_benchmark(used, benchmark, obj):
    if used == benchmark:
        print(f"[ {color('bright yellow')}BENCHMARK MATCHED {color}]")
    elif used < benchmark:
        save_benchmark_to_file(inspect.stack()[1].function, obj, used)
        print(f"[ {color('dark green')}BENCHMARK BEATEN BY {benchmark-used}{color} ]")
    else:
        print(f"[ {color('bright red')}BENCHMARK MISSED BY {used-benchmark}{color} ]")


def params_from_file():
    with Path(__file__).parent.absolute().joinpath(Path("benchmarks.json")).open() as fp:
        benchmarks = json.load(fp)
    return benchmarks


PARAMS = params_from_file()


def save_benchmark_to_file(function, obj, new_benchmark):
    if not UPDATE_BENCHMARKS:
        return
    benchmarks = params_from_file()
    objs = benchmarks.setdefault(function, [])
    updated_obj = obj.copy()
    updated_obj["gas"] = new_benchmark
    found = False
    for i, entry in enumerate(objs):
        if entry["amount"] == obj["amount"]:
            objs[i] = updated_obj
            found = True
            break
    if not found:
        objs.append(updated_obj)

    with Path(__file__).parent.absolute().joinpath(Path("benchmarks.json")).open("w") as fp:
        json.dump(benchmarks, fp)


def test_setup(liquid_lgt, accounts):
    assert liquid_lgt.totalSupply() == 160
    assert liquid_lgt.ownedSupply() == 68
    assert liquid_lgt.balanceOf(accounts[0]) == 30
    assert liquid_lgt.balanceOf(accounts[1]) == 38
    assert liquid_lgt.poolTokenReserves() == 92


@pytest.mark.parametrize("params", PARAMS['test_mint'])
def test_mint(liquid_lgt, accounts, params):
    tx_mint = liquid_lgt.mint(params["amount"], {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    process_benchmark(gas_mint, params['gas'], params)
    print(f"Gas Paid: {gas_mint} for {params['amount']} tokens.")
    assert gas_mint <= params["gas"]


@pytest.mark.parametrize("params", PARAMS['test_mint_to_sell'])
def test_mint_to_sell(liquid_lgt, accounts, params):
    initial_balance = accounts[0].balance()
    tx_mint = liquid_lgt.mintToSell(params["amount"], 1, DEADLINE, {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    process_benchmark(gas_mint, params['gas'], params)
    print(f"Gas Paid: {gas_mint}. Minted {params['amount']} tokens.")
    assert gas_mint <= params["gas"]
    assert accounts[0].balance() > initial_balance


@pytest.mark.parametrize("params", PARAMS['test_mint_to_sell_to'])
def test_mint_to_sell_to(liquid_lgt, accounts, params):
    initial_balance = accounts[1].balance()
    tx_mint = liquid_lgt.mintToSellTo(params["amount"], 1, DEADLINE, accounts[1], {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    process_benchmark(gas_mint, params['gas'], params)
    print(f"Gas Paid: {gas_mint}. Minted and sold {params['amount']} tokens.")
    assert gas_mint <= params["gas"]
    assert accounts[1].balance() > initial_balance


@pytest.mark.parametrize("params", PARAMS['test_mint_to_liquidity'])
def test_mint_to_liquidity(liquid_lgt, accounts, params):
    initial_shares = liquid_lgt.poolBalanceOf(accounts[1])
    tx_mint = liquid_lgt.mintToLiquidity(
        params["amount"],
        1,
        DEADLINE,
        accounts[1],
        {'from': accounts[0], 'value': params["eth"]}
    )
    gas_mint = tx_mint.gas_used
    tokens, eth, shares = tx_mint.return_value
    assert tokens == params['amount']
    assert eth == params['eth']
    assert shares == params['eth']
    process_benchmark(gas_mint, params['gas'], params)
    print(f"Gas Paid: {gas_mint}. Minted and added {params['amount']} tokens and {params['eth']} wei.")
    assert gas_mint <= params["gas"]
    assert liquid_lgt.poolBalanceOf(accounts[1]) > initial_shares
