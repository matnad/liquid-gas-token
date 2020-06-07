from brownie import *
import brownie

DEADLINE = 99999999999


def test_token_constraint(lgt, accounts):
    tx = lgt.mintToLiquidity(4, 0, DEADLINE, accounts[5], {'from': accounts[5], 'value': "0.1 ether"})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == 4
    assert eth_added == Wei("0.004 ether") - 1
    assert liq_added == Wei("0.004 ether") - 1
    assert lgt.balance() == Wei("0.005 ether") - 1
    assert lgt.ownedSupply() == 30


def test_eth_constraint(lgt, accounts):
    tx = lgt.mintToLiquidity(100, 0, DEADLINE, accounts[5], {'from': accounts[5], 'value': Wei("0.01 ether") - 1})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == 10
    assert eth_added == Wei("0.01 ether") - 1
    assert liq_added == Wei("0.01 ether") - 1
    assert lgt.balance() == Wei("0.011 ether") - 1
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.011 ether") - 1


def test_exact(lgt, accounts):
    tx = lgt.mintToLiquidity(15, 0, DEADLINE, accounts[5], {'from': accounts[5], 'value': Wei("0.015 ether") - 1})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == 15
    assert eth_added == Wei("0.015 ether") - 1
    assert liq_added == Wei("0.015 ether") - 1
    assert lgt.balance() == Wei("0.016 ether") - 1
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.016 ether") - 1


def test_refund(lgt, accounts):
    initial_balance = accounts[5].balance()
    tx = lgt.mintToLiquidity(15, 0, DEADLINE, accounts[5], {'from': accounts[5], 'value': Wei("2 ether")})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == 15
    assert eth_added == Wei("0.015 ether") - 1
    assert liq_added == Wei("0.015 ether") - 1
    assert initial_balance - accounts[5].balance() == eth_added
    assert lgt.balance() == Wei("0.016 ether") - 1
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.016 ether") - 1


def test_deadline_reverts(lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        lgt.mintToLiquidity(10, 0, 1, accounts[4], {'from': accounts[4], 'value': "0.1 ether"})


def test_min_token_reverts(lgt, accounts):
    with brownie.reverts("dev: can't mint less than 1 token"):
        lgt.mintToLiquidity(0, 0, DEADLINE, accounts[4], {'from': accounts[4], 'value': "0.1 ether"})


def test_no_eth_reverts(lgt, accounts):
    with brownie.reverts("dev: must provide ether to add liquidity"):
        lgt.mintToLiquidity(10, 0, DEADLINE, accounts[4], {'from': accounts[4]})

