from brownie import *
import brownie


def test_mint_to_empty_liquidity(lgt, accounts):
    token_amount = 10
    eth_amount = Wei("0.1 ether")
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == 0
    tx = lgt.mintToLiquidity(token_amount, 0, 99999999999999, {'from': accounts[4], 'value': eth_amount})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == token_amount
    assert eth_added == eth_amount
    assert liq_added == eth_amount
    assert lgt.ownedSupply() == 30
    assert lgt.totalSupply() - lgt.ownedSupply() == token_amount
    assert lgt.poolTotalSupply() == eth_amount
    assert lgt.balance() == eth_amount


def test_mint_to_liquidity_token_constraint(lgt, accounts):
    lgt.mintToLiquidity(10, 0, 99999999999999, {'from': accounts[4], 'value': "0.1 ether"})
    tx = lgt.mintToLiquidity(4, 0, 99999999999999, {'from': accounts[5], 'value': "0.1 ether"})
    tokens_added, eth_added, liq_added = tx.return_value
    assert tokens_added == 4
    assert eth_added == Wei("0.04 ether") - 1
    assert liq_added == Wei("0.04 ether") - 1
    assert lgt.balance() == Wei("0.14 ether") - 1
    assert lgt.totalSupply() == 44
    assert lgt.ownedSupply() == 30


def test_mint_to_liquidity_eth_constraint(lgt, accounts):
    lgt.mintToLiquidity(10, 0, 99999999999999, {'from': accounts[4], 'value': "0.1 ether"})
    tx = lgt.mintToLiquidity(100, 0, 99999999999999, {'from': accounts[5], 'value': Wei("0.1 ether")})
    tokens_added, eth_added, liq_added = tx.return_value
    # print(tokens_added, eth_added.to("ether"), liq_added.to("ether"), accounts[5].balance().to("ether"))
    assert tokens_added == 10
    assert eth_added == Wei("0.1 ether") - 1
    assert liq_added == Wei("0.1 ether") - 1
    assert lgt.balance() == Wei("0.2 ether") - 1
    assert lgt.totalSupply() == 50
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.2 ether") - 1


def test_mint_to_liquidity_exact(lgt, accounts):
    lgt.mintToLiquidity(10, 0, 99999999999999, {'from': accounts[4], 'value': "0.1 ether"})
    tx = lgt.mintToLiquidity(15, 0, 99999999999999, {'from': accounts[5], 'value': Wei("0.15 ether") - 1})
    tokens_added, eth_added, liq_added = tx.return_value
    # print(tokens_added, eth_added.to("ether"), liq_added.to("ether"), accounts[5].balance().to("ether"))
    assert tokens_added == 15
    assert eth_added == Wei("0.15 ether") - 1
    assert liq_added == Wei("0.15 ether") - 1
    assert lgt.balance() == Wei("0.25 ether") - 1
    assert lgt.totalSupply() == 55
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.25 ether") - 1


def test_mint_to_empty_liquidity_reverts(lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        lgt.mintToLiquidity(10, 0, 1, {'from': accounts[4], 'value': "0.1 ether"})
    with brownie.reverts("dev: can't mint less than 1 token"):
        lgt.mintToLiquidity(0, 0, 99999999999999, {'from': accounts[4], 'value': "0.1 ether"})
    with brownie.reverts("dev: must provide ether to add liquidity"):
        lgt.mintToLiquidity(10, 0, 99999999999999, {'from': accounts[4]})
    with brownie.reverts("dev: initial eth below 1 gwei"):
        lgt.mintToLiquidity(10, 0, 99999999999999, {'from': accounts[4], 'value': "0.5 gwei"})

