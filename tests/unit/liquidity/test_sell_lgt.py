#!/usr/bin/python3
import brownie
import pytest
from brownie import *
from brownie.test import given
from hypothesis import settings, strategies as st

DEADLINE = 99999999999
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
FEE_MODIFIER = 995
mint = 60
TOKEN_RESERVE = 70
ETH_RESERVE = Wei("0.069 ether")

account5_supply = 80


def token_to_eth_output(token_amount_to_sell: int) -> "Wei":
    """ Constant Price Model implementation with fee. """
    input_amount_with_fee = token_amount_to_sell * FEE_MODIFIER
    numerator = input_amount_with_fee * ETH_RESERVE
    denominator = TOKEN_RESERVE * 1000 + input_amount_with_fee
    return Wei(numerator // denominator)


def token_to_eth_input(eth_amount_to_buy: int) -> "Wei":
    """ Constant Price Model implementation with fee. """
    numerator = TOKEN_RESERVE * eth_amount_to_buy * 1000
    denominator = (ETH_RESERVE - eth_amount_to_buy) * FEE_MODIFIER
    return Wei(numerator // denominator + 1)


st_sell_amount_token = st.integers(min_value=1, max_value=account5_supply)
st_buy_amount_eth = st.integers(
    min_value=int(Wei("1 gwei")),
    max_value=int(token_to_eth_output(account5_supply))
)


@pytest.fixture(scope="module")
def liquidLgt(lgt, accounts):
    lgt.mint(mint, {'from': accounts[0]})
    lgt.mint(account5_supply, {'from': accounts[5]})
    lgt.addLiquidity(1, TOKEN_RESERVE - 1, DEADLINE, {'from': accounts[0], 'value': ETH_RESERVE - "0.001 ether"})
    yield lgt


@given(sell_amount=st_sell_amount_token)
@settings(max_examples=20)
def test_sell_lgt_input(liquidLgt, accounts, sell_amount):
    initial_balance = accounts[5].balance()
    initial_reserve = liquidLgt.balance()

    eth_bought = token_to_eth_output(sell_amount)
    tx = liquidLgt.tokenToEthSwapInput(sell_amount, 1, DEADLINE, {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - sell_amount
    assert tx.return_value == int(eth_bought)
    assert initial_balance + eth_bought == accounts[5].balance()
    assert initial_reserve - eth_bought == liquidLgt.balance()


@given(sell_amount=st_sell_amount_token)
@settings(max_examples=5)
def test_sell_lgt_input_to(liquidLgt, accounts, sell_amount):
    initial_balance = accounts[3].balance()
    eth_bought = token_to_eth_output(sell_amount)
    eth_bought_solidity = liquidLgt.getTokenToEthInputPrice(sell_amount)
    tx = liquidLgt.tokenToEthTransferInput(sell_amount, 1, DEADLINE, accounts[3], {'from': accounts[5]})
    assert tx.return_value == eth_bought
    assert tx.return_value == eth_bought_solidity
    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - sell_amount
    assert tx.return_value == accounts[3].balance() - initial_balance


def test_input_deadline_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.tokenToEthSwapInput(1, 1, 1, {'from': accounts[5]})


def test_input_exceed_reverts(liquidLgt, accounts):
    with brownie.reverts("LGT: amount exceeds balance"):
        liquidLgt.tokenToEthSwapInput(1, 1, DEADLINE, {'from': accounts[6]})


def test_input_tokens_sold_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: must sell one or more tokens"):
        liquidLgt.tokenToEthSwapInput(0, 1, DEADLINE, {'from': accounts[5]})


def test_input_no_min_eth_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: minEth not set"):
        liquidLgt.tokenToEthSwapInput(1, 0, DEADLINE, {'from': accounts[5]})


def test_input_minethlow_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: tokens not worth enough"):
        liquidLgt.tokenToEthSwapInput(1, "100 ether", DEADLINE, {'from': accounts[5]})


def test_input_to_lgt_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.tokenToEthTransferInput(1, 1, DEADLINE, liquidLgt.address, {'from': accounts[5]})


def test_input_to_zero_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.tokenToEthTransferInput(1, 1, DEADLINE, ZERO_ADDRESS, {'from': accounts[5]})


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=20)
def test_sell_lgt_output(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[5].balance()
    initial_reserve = liquidLgt.balance()

    tokens_sold = token_to_eth_input(buy_amount)
    assert tokens_sold == liquidLgt.getTokenToEthOutputPrice(buy_amount)
    tx = liquidLgt.tokenToEthSwapOutput(buy_amount, 999, DEADLINE, {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - tokens_sold
    assert initial_balance + buy_amount == accounts[5].balance()
    assert initial_reserve - buy_amount == liquidLgt.balance()
    assert tx.return_value == tokens_sold


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=5)
def test_sell_lgt_output_to(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[3].balance()
    initial_reserve = liquidLgt.balance()

    tokens_sold = token_to_eth_input(buy_amount)
    assert tokens_sold == liquidLgt.getTokenToEthOutputPrice(buy_amount)
    tx = liquidLgt.tokenToEthTransferOutput(buy_amount, 999, DEADLINE, accounts[3], {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - tokens_sold
    assert initial_balance + buy_amount == accounts[3].balance()
    assert initial_reserve - buy_amount == liquidLgt.balance()
    assert tx.return_value == tokens_sold


def test_output_deadline_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.tokenToEthSwapOutput(1, 1, 1, {'from': accounts[5]})


def test_output_exceed_reverts(liquidLgt, accounts):
    with brownie.reverts("LGT: amount exceeds balance"):
        liquidLgt.tokenToEthSwapOutput(1, 1, DEADLINE, {'from': accounts[6]})


def test_output_eth_bought_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: must buy more than 0 eth"):
        liquidLgt.tokenToEthSwapOutput(0, 1, DEADLINE, {'from': accounts[5]})


def test_output_max_tokens_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: need more tokens to sell"):
        liquidLgt.tokenToEthSwapOutput(1, 0, DEADLINE, {'from': accounts[5]})


def test_output_to_lgt_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.tokenToEthTransferOutput(1, 1, DEADLINE, liquidLgt.address, {'from': accounts[5]})


def test_output_to_zero_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.tokenToEthTransferOutput(1, 1, DEADLINE, ZERO_ADDRESS, {'from': accounts[5]})
