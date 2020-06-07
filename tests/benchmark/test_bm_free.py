import json
from pathlib import Path
import inspect

import pytest
from brownie import *
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
        if entry["burn"] == obj["burn"] and entry["free"] == obj["free"]:
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


@pytest.mark.parametrize("params", PARAMS['test_burn_and_free_from'])
def test_burn_and_free_from(liquid_lgt, helper, accounts, params):
    liquid_lgt.mint(params['free'], {'from': accounts[0]})
    tx_free = helper.burnAndFree(params['burn'], params['free'], {'from': accounts[0]})
    gas_paid = tx_free.gas_used
    process_benchmark(gas_paid, params['gas'], params)
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with {params['free']} owned tokens.")
    assert gas_paid <= params["gas"]


@pytest.mark.parametrize("params", PARAMS['test_burn_buy_and_free_exact'])
def test_burn_buy_and_free_exact(liquid_lgt, helper, accounts, params):
    initial_balance = accounts[0].balance()
    price = liquid_lgt.getEthToTokenOutputPrice(params['free'])
    tx_free = helper.burnBuyAndFree(params['burn'], params['free'], {'from': accounts[0], 'value': price})
    gas_paid = tx_free.gas_used
    process_benchmark(gas_paid, params['gas'], params)
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with {params['free']} bought tokens.")
    assert gas_paid <= params["gas"]
    assert accounts[0].balance() < initial_balance


@pytest.mark.parametrize("params", PARAMS['test_burn_buy_up_to_and_free'])
def test_burn_buy_up_to_and_free(liquid_lgt, helper, accounts, params):
    initial_balance = accounts[0].balance()
    tx_free = helper.burnBuyUpToAndFree(params['burn'], params['free'], {'from': accounts[0], 'value': "5 ether"})
    gas_paid = tx_free.gas_used
    process_benchmark(gas_paid, params['gas'], params)
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with (up to) {params['free']} bought tokens.")
    assert gas_paid <= params["gas"]
    assert accounts[0].balance() < initial_balance

