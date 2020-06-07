from brownie import *
import brownie


DEADLINE = 99999999999


# TODO: Parametrize
def test_add_liquidity_eth_constraint(lgt, accounts):
    lgt.mint(15, {'from': accounts[1]})
    tx = lgt.addLiquidity("0.005 ether", 15, DEADLINE, {'from': accounts[1], 'value': "0.005 ether"})
    # tokens = 0.005 / 0.001 + 1 = 6
    # Should add 0.005 ether and 6 tokens to liquidity
    assert tx.return_value == Wei("0.005 ether")
    event = tx.events['AddLiquidity']
    assert event["provider"] == accounts[1]
    assert event["eth_amount"] == "0.005 ether"
    assert event["token_amount"] == 6
    assert lgt.poolTotalSupply() == Wei("0.006 ether")
    assert lgt.balanceOf(accounts[1]) == 15 - 6
    assert lgt.ownedSupply() == 30 + 15 - 6


def test_add_liquidity_exact(lgt, accounts):
    lgt.mint(9, {'from': accounts[1]})
    tx = lgt.addLiquidity("0.008 ether", 9, DEADLINE, {'from': accounts[1], 'value': "0.008 ether"})
    # tokens = 0.008 / 0.001 + 1 = 9
    # Should add 0.008 ether and 9 tokens to liquidity
    assert tx.return_value == Wei("0.008 ether")
    assert lgt.poolTotalSupply() == Wei("0.009 ether")
    assert lgt.balanceOf(accounts[1]) == 0
    assert lgt.ownedSupply() == 30


def test_add_liquidity_insufficient_lgt(lgt, accounts):
    lgt.mint(15, {'from': accounts[1]})
    with brownie.reverts('dev: need more tokens'):
        tx = lgt.addLiquidity("0.1 ether", 15, DEADLINE, {'from': accounts[1], 'value': "0.1 ether"})
        assert tx.return_value == 0
        # tokens = 0.1 / 0.001 + 1 = 101
        # Needs 101 tokens to add 0.1 ether liquidity
    assert lgt.poolTotalSupply() == "0.001 ether"
    assert lgt.balanceOf(accounts[1]) == 15


def test_add_liquidity_insufficient_liquidity(lgt, accounts):
    lgt.mint(15, {'from': accounts[1]})
    with brownie.reverts('dev: not enough liquidity can be created'):
        tx = lgt.addLiquidity("0.01 ether", 9, DEADLINE, {'from': accounts[1], 'value': "0.008 ether"})
        assert tx.return_value == 0
        # Would create 0.008 liquidity, bit minimum 0.01 is requested
    assert lgt.poolTotalSupply() == Wei("0.001 ether")
    assert lgt.balanceOf(accounts[1]) == 15
