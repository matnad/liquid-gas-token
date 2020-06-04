#!/usr/bin/python3
import brownie
import pytest
from brownie import *
from brownie.test import given
from hypothesis import settings, strategies as st


mint = 60
token_liquidity = 70
eth_liquidity = Wei("3 ether")

account5_supply = 80


def sell_token_amount_to_eth(sell_amount: int) -> "Wei":
    input_amount_with_fee = sell_amount * 995
    numerator = input_amount_with_fee * eth_liquidity
    denominator = token_liquidity * 1000 + input_amount_with_fee
    return Wei(numerator // denominator)


def buy_eth_amount_for_tokens(buy_amount: int) -> "Wei":
    numerator = token_liquidity * buy_amount * 1000
    denominator = (eth_liquidity - buy_amount) * 995
    return Wei(numerator // denominator + 1)


st_sell_amount_token = st.integers(min_value=1, max_value=account5_supply)
st_buy_amount_eth = st.integers(
    min_value=int(Wei("1 gwei")),
    max_value=int(sell_token_amount_to_eth(account5_supply))
)


@pytest.fixture(scope="module")
def liquidLgt(lgt, accounts):
    lgt.mint(mint, {'from': accounts[0]})
    lgt.mint(account5_supply, {'from': accounts[5]})
    lgt.addLiquidity(0, token_liquidity, 99999999999, {'from': accounts[0], 'value': eth_liquidity})
    yield lgt


@given(sell_amount=st_sell_amount_token)
@settings(max_examples=20)
def test_sell_lgt_input(liquidLgt, accounts, sell_amount):
    initial_balance = accounts[5].balance()
    initial_reserve = liquidLgt.balance()

    eth_bought = sell_token_amount_to_eth(sell_amount)
    tx = liquidLgt.tokenToEthSwapInput(sell_amount, 1, 99999999999, {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - sell_amount
    assert tx.return_value == int(eth_bought)
    assert initial_balance + eth_bought == accounts[5].balance()
    assert initial_reserve - eth_bought == liquidLgt.balance()


@given(sell_amount=st_sell_amount_token)
@settings(max_examples=5)
def test_sell_lgt_input_to(liquidLgt, accounts, sell_amount):
    initial_balance = accounts[3].balance()
    eth_bought = sell_token_amount_to_eth(sell_amount)
    eth_bought_solidity = liquidLgt.getTokenToEthInputPrice(sell_amount)
    tx = liquidLgt.tokenToEthTransferInput(sell_amount, 1, 99999999999, accounts[3], {'from': accounts[5]})
    assert tx.return_value == eth_bought
    assert tx.return_value == eth_bought_solidity
    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - sell_amount
    assert tx.return_value == accounts[3].balance() - initial_balance


def test_sell_lgt_input_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.tokenToEthSwapInput(1, 1, 1, {'from': accounts[5]})
    with brownie.reverts("ERC20: unassign amount exceeds balance"):
        liquidLgt.tokenToEthSwapInput(1, 1, 99999999999, {'from': accounts[6]})
    with brownie.reverts("dev: must sell one or more tokens"):
        liquidLgt.tokenToEthSwapInput(0, 1, 99999999999, {'from': accounts[5]})
    with brownie.reverts("dev: minEth not set"):
        liquidLgt.tokenToEthSwapInput(1, 0, 99999999999, {'from': accounts[5]})
    with brownie.reverts("dev: tokens not worth enough"):
        liquidLgt.tokenToEthSwapInput(1, "100 ether", 99999999999, {'from': accounts[5]})
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.tokenToEthTransferInput(1, 1, 99999999999, liquidLgt.address, {'from': accounts[5]})
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.tokenToEthTransferInput(1, 1, 99999999999, "0x0000000000000000000000000000000000000000", {'from': accounts[5]})


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=20)
def test_sell_lgt_output(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[5].balance()
    initial_reserve = liquidLgt.balance()

    tokens_sold = buy_eth_amount_for_tokens(buy_amount)
    assert tokens_sold == liquidLgt.getTokenToEthOutputPrice(buy_amount)
    tx = liquidLgt.tokenToEthSwapOutput(buy_amount, 999, 99999999999, {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - tokens_sold
    assert initial_balance + buy_amount == accounts[5].balance()
    assert initial_reserve - buy_amount == liquidLgt.balance()
    assert tx.return_value == tokens_sold


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=5)
def test_sell_lgt_output_to(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[3].balance()
    initial_reserve = liquidLgt.balance()

    tokens_sold = buy_eth_amount_for_tokens(buy_amount)
    assert tokens_sold == liquidLgt.getTokenToEthOutputPrice(buy_amount)
    tx = liquidLgt.tokenToEthTransferOutput(buy_amount, 999, 99999999999, accounts[3], {'from': accounts[5]})

    assert liquidLgt.balanceOf(accounts[5]) == account5_supply - tokens_sold
    assert initial_balance + buy_amount == accounts[3].balance()
    assert initial_reserve - buy_amount == liquidLgt.balance()
    assert tx.return_value == tokens_sold


def test_sell_lgt_output_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.tokenToEthSwapOutput(1, 1, 1, {'from': accounts[5]})
    with brownie.reverts("ERC20: unassign amount exceeds balance"):
        liquidLgt.tokenToEthSwapOutput(1, 1, 99999999999, {'from': accounts[6]})
    with brownie.reverts("dev: must buy more than 0 eth"):
        liquidLgt.tokenToEthSwapOutput(0, 1, 99999999999, {'from': accounts[5]})
    with brownie.reverts("dev: need more tokens to sell"):
        liquidLgt.tokenToEthSwapOutput(1, 0, 99999999999, {'from': accounts[5]})
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.tokenToEthTransferOutput(1, 1, 99999999999, liquidLgt.address, {'from': accounts[5]})
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.tokenToEthTransferOutput(1, 1, 99999999999, "0x0000000000000000000000000000000000000000", {'from': accounts[5]})
