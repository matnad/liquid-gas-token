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
        {'amount': 1, 'gas': 75622},
        {'amount': 10, 'gas': 404023},
        {'amount': 32, 'gas': 1205390},
        {'amount': 71, 'gas': 2627070}
    ]
)
def test_mint(liquid_lgt, accounts, params):
    tx_mint = liquid_lgt.mint(params["amount"], {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    print(f"Gas Paid: {gas_mint} for {params['amount']} tokens.")
    assert gas_mint <= params["gas"]


@pytest.mark.parametrize(
    "params", [
        {'amount': 1, 'gas': 74669},
        {'amount': 10, 'gas': 403070},
        {'amount': 32, 'gas': 1204437},
        {'amount': 71, 'gas': 2626117}
    ]
)
def test_mint_to_sell(liquid_lgt, accounts, params):
    initial_balance = accounts[0].balance()
    tx_mint = liquid_lgt.mintToSell(params["amount"], 1, DEADLINE, {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    print(f"Gas Paid: {gas_mint}. Minted {params['amount']} tokens.")
    assert gas_mint <= params["gas"]
    assert accounts[0].balance() > initial_balance


@pytest.mark.parametrize(
    "params", [
        {'amount': 1, 'gas': 75067},
        {'amount': 10, 'gas': 403468},
        {'amount': 32, 'gas': 1204835},
        {'amount': 71, 'gas': 2626515}
    ]
)
def test_mint_to_sell_to(liquid_lgt, accounts, params):
    initial_balance = accounts[1].balance()
    tx_mint = liquid_lgt.mintToSellTo(params["amount"], 1, DEADLINE, accounts[1], {'from': accounts[0]})
    gas_mint = tx_mint.gas_used
    print(f"Gas Paid: {gas_mint}. Minted and sold {params['amount']} tokens.")
    assert gas_mint <= params["gas"]
    assert accounts[1].balance() > initial_balance


@pytest.mark.parametrize(
    "params", [
        {'amount': 1, 'eth': 5978260869565216, 'gas': 83204},
        {'amount': 10, 'eth': 59782608695652172, 'gas': 411605},
        {'amount': 32, 'eth': 191304347826086955, 'gas': 1212972},
        {'amount': 71, 'eth': 424456521739130433, 'gas': 2634652}
    ]
)
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
    print(f"Gas Paid: {gas_mint}. Minted and added {params['amount']} tokens and {params['eth']} wei.")
    assert gas_mint <= params["gas"]
    assert liquid_lgt.poolBalanceOf(accounts[1]) > initial_shares
