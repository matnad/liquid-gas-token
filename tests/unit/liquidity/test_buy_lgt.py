#!/usr/bin/python3
import brownie
import pytest
from brownie import *
from brownie.test import given
from hypothesis import settings, strategies as st


mint = 60
token_liquidity = 80
eth_liquidity = Wei("5 ether")

st_buy_amount_eth = st.integers(min_value=int(Wei("1 gwei")), max_value=int(Wei("10 ether")))
st_buy_amount_token = st.integers(min_value=1, max_value=int(token_liquidity*0.9))


def buy_amount_to_tokens(buy_amount: "Wei") -> "Wei":
    input_amount_with_fee = buy_amount * 995
    numerator = input_amount_with_fee * token_liquidity
    denominator = eth_liquidity * 1000 + input_amount_with_fee
    return Wei(numerator // denominator)


@pytest.fixture(scope="module")
def liquidLgt(lgt, accounts):
    lgt.mint(mint, {'from': accounts[0]})
    lgt.addLiquidity(0, token_liquidity, 99999999999, {'from': accounts[0], 'value': eth_liquidity})
    yield lgt


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=50)
def test_buy_lgt_atleast(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[2].balance()
    initial_reserve = liquidLgt.balance()
    token_amount = buy_amount_to_tokens(buy_amount)

    if token_amount >= 1:
        tx = liquidLgt.ethToTokenSwapInput(1, 99999999999, {'from': accounts[2], 'value': buy_amount})
        assert liquidLgt.balanceOf(accounts[2]) == int(token_amount)
        assert tx.return_value == int(token_amount)
        assert initial_balance - buy_amount == accounts[2].balance()
        assert initial_reserve + buy_amount == liquidLgt.balance()
    else:
        with brownie.reverts("dev: not enough eth to buy tokens"):
            liquidLgt.ethToTokenSwapInput(1, 99999999999, {'from': accounts[2], 'value': buy_amount})


@given(buy_amount=st_buy_amount_eth)
@settings(max_examples=5)
def test_buy_lgt_atleast_for(liquidLgt, accounts, buy_amount):
    token_amount = buy_amount_to_tokens(buy_amount)
    if token_amount >= 1:
        tx = liquidLgt.ethToTokenTransferInput(1, 99999999999, accounts[3], {'from': accounts[2], 'value': buy_amount})
        assert tx.return_value == token_amount
        assert liquidLgt.balanceOf(accounts[3]) == token_amount


def test_buy_lgt_at_least_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.ethToTokenTransferInput(1, 1, accounts[3], {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("dev: no eth to sell"):
        liquidLgt.ethToTokenTransferInput(1, 99999999999, accounts[3], {'from': accounts[2], 'value': "0 ether"})
    with brownie.reverts("dev: must buy one or more tokens"):
        liquidLgt.ethToTokenTransferInput(0, 99999999999, accounts[3], {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("dev: not enough eth to buy tokens"):
        liquidLgt.ethToTokenTransferInput(25, 99999999999, accounts[3], {'from': accounts[2], 'value': "0.2 ether"})


@given(buy_amount=st_buy_amount_token)
@settings(max_examples=10)
def test_buy_lgt_exact(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[2].balance()
    eth_sold = liquidLgt.getEthToTokenOutputPrice(buy_amount)
    tx = liquidLgt.ethToTokenSwapOutput(buy_amount, 99999999999, {'from': accounts[2], 'value': "50 ether"})
    assert liquidLgt.balanceOf(accounts[2]) == buy_amount
    assert tx.return_value == eth_sold
    assert initial_balance - tx.return_value == accounts[2].balance()


@given(buy_amount=st_buy_amount_token)
@settings(max_examples=5)
def test_buy_lgt_exact_for(liquidLgt, accounts, buy_amount):
    initial_balance = accounts[2].balance()
    eth_sold = liquidLgt.getEthToTokenOutputPrice(buy_amount)
    tx = liquidLgt.ethToTokenTransferOutput(buy_amount, 99999999999, accounts[3], {'from': accounts[2], 'value': "50 ether"})
    assert liquidLgt.balanceOf(accounts[3]) == buy_amount
    assert tx.return_value == eth_sold
    assert initial_balance - tx.return_value == accounts[2].balance()


def test_buy_lgt_exact_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.ethToTokenTransferOutput(1, 1, liquidLgt, {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.ethToTokenTransferOutput(1, 1, "0x0000000000000000000000000000000000000000", {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.ethToTokenTransferOutput(1, 1, accounts[3], {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("dev: maxEth must greater than 0"):
        liquidLgt.ethToTokenTransferOutput(1, 99999999999, accounts[3], {'from': accounts[2], 'value': "0 ether"})
    with brownie.reverts("dev: must buy one or more tokens"):
        liquidLgt.ethToTokenTransferOutput(0, 99999999999, accounts[3], {'from': accounts[2], 'value': "0.2 ether"})
    with brownie.reverts("LGT: not enough ETH to buy tokens"):
        liquidLgt.ethToTokenTransferOutput(25, 99999999999, accounts[3], {'from': accounts[2], 'value': "0.01 ether"})
