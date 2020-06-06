import pytest
from brownie import *


DEADLINE = 999999999999999


def test_setup(liquid_lgt, accounts):
    assert liquid_lgt.totalSupply() == 160
    assert liquid_lgt.ownedSupply() == 68
    assert liquid_lgt.balanceOf(accounts[0]) == 30
    assert liquid_lgt.balanceOf(accounts[1]) == 38
    assert liquid_lgt.poolTokenReserves() == 92


@pytest.mark.parametrize(
    "params", [
        {'burn': 1e5, 'free': 4, 'gas': 86623},
        {'burn': 5e5, 'free': 12, 'gas': 332072},
        {'burn': 1e6, 'free': 25, 'gas': 598102},
        {'burn': 2e6, 'free': 50, 'gas': 1171290},
    ]
)
def test_burn_and_free_from(liquid_lgt, helper, accounts, params):
    liquid_lgt.mint(params['free'], {'from': accounts[0]})
    tx_free = helper.burnAndFree(params['burn'], params['free'], {'from': accounts[0]})
    gas_paid = tx_free.gas_used
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with {params['free']} owned tokens.")
    assert gas_paid <= params["gas"]


@pytest.mark.parametrize(
    "params", [
        {'burn': 1e5, 'free': 4, 'gas': 81582},
        {'burn': 5e5, 'free': 12, 'gas': 321990},
        {'burn': 1e6, 'free': 25, 'gas': 593061},
        {'burn': 2e6, 'free': 50, 'gas': 1166249},
    ]
)
def test_burn_buy_and_free_exact(liquid_lgt, helper, accounts, params):
    initial_balance = accounts[0].balance()
    price = liquid_lgt.getEthToTokenOutputPrice(params['free'])
    tx_free = helper.burnBuyAndFree(params['burn'], params['free'], {'from': accounts[0], 'value': price})
    gas_paid = tx_free.gas_used
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with {params['free']} bought tokens.")
    assert gas_paid <= params["gas"]
    assert accounts[0].balance() < initial_balance


@pytest.mark.parametrize(
    "params", [
        {'burn': 1e5, 'free': 4, 'gas': 81461},
        {'burn': 5e5, 'free': 12, 'gas': 321748},
        {'burn': 1e6, 'free': 25, 'gas': 592940},
        {'burn': 2e6, 'free': 50, 'gas': 1166128},
    ]
)
def test_burn_buy_up_to_and_free(liquid_lgt, helper, accounts, params):
    initial_balance = accounts[0].balance()
    tx_free = helper.burnBuyUpToAndFree(params['burn'], params['free'], {'from': accounts[0], 'value': "5 ether"})
    gas_paid = tx_free.gas_used
    print(f"Gas Paid: {gas_paid}/{int(params['burn'])} with (up to) {params['free']} bought tokens.")
    assert gas_paid <= params["gas"]
    assert accounts[0].balance() < initial_balance

