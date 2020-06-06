from brownie import *
import brownie


# TODO: Parametrize
def test_add_first_liquidity(lgt, accounts):
    assert lgt.ownedSupply() == 30
    assert lgt.poolTotalSupply() == 0
    tx = lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    event = tx.events['AddLiquidity']
    assert event["provider"] == accounts[0]
    assert event["eth_amount"] == "0.5 ether"
    assert event["token_amount"] == 10
    assert tx.return_value == Wei("0.5 ether")
    assert lgt.ownedSupply() == 20
    assert lgt.totalSupply() == 30
    assert lgt.poolTotalSupply() == Wei("0.5 ether")


# TODO: Parametrize
def test_add_liquidity_eth_constraint(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    lgt.mint(15, {'from': accounts[1]})
    tx = lgt.addLiquidity("0.1 ether", 15, 99999999999, {'from': accounts[1], 'value': "0.1 ether"})
    # uint256 ethReserve = address(this).balance - msg.value;  -> 0.5 ether
    # uint256 tokenReserve = totalSupply() - ownedSupply(); -> 10
    # uint256 tokenAmount = msg.value.mul(tokenReserve).div(ethReserve).add(1); 0.1 * 10 / 0.5 + 1 = 1 / 0.5 + 1 = 3
    # uint256 liquidityCreated = msg.value.mul(totalLiquidity).div(ethReserve); 0.1 * 0.5 / 0.5 = 0.1
    # Should add 0.1 ether and 3 tokens to liquidity
    assert tx.return_value == Wei("0.1 ether")
    event = tx.events['AddLiquidity']
    assert event["provider"] == accounts[1]
    assert event["eth_amount"] == "0.1 ether"
    assert event["token_amount"] == 3
    assert lgt.poolTotalSupply() == Wei("0.6 ether")
    assert lgt.balanceOf(accounts[1]) == 15 - 3
    assert lgt.totalSupply() == 45
    assert lgt.ownedSupply() == 20 + 15 - 3


# TODO: Parametrize
def test_add_liquidity_exact(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    lgt.mint(15, {'from': accounts[1]})
    tx = lgt.addLiquidity("0.7 ether", 15, 99999999999, {'from': accounts[1], 'value': "0.7 ether"})
    # uint256 ethReserve = address(this).balance - msg.value;  -> 0.5 ether
    # uint256 tokenReserve = totalSupply() - ownedSupply(); -> 10
    # uint256 tokenAmount = msg.value.mul(tokenReserve).div(ethReserve).add(1); 0.7 * 10 / 0.5 + 1 = 7 / 0.5 + 1 = 15
    # uint256 liquidityCreated = msg.value.mul(totalLiquidity).div(ethReserve); 0.7 * 0.5 / 0.5 = 0.7
    # Should add 0.7 ether and 15 tokens to liquidity
    assert tx.return_value == Wei("0.7 ether")
    assert lgt.poolTotalSupply() == Wei("1.2 ether")
    assert lgt.balanceOf(accounts[1]) == 0
    assert lgt.totalSupply() == 45
    assert lgt.ownedSupply() == 20


def test_add_liquidity_insufficient_lgt(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    lgt.mint(15, {'from': accounts[1]})

    with brownie.reverts('dev: need more tokens'):
        tx = lgt.addLiquidity("1 ether", 15, 99999999999, {'from': accounts[1], 'value': "1 ether"})
        assert tx.return_value == 0
        # uint256 ethReserve = address(this).balance - msg.value;  -> 0.5 ether
        # uint256 tokenReserve = totalSupply() - ownedSupply(); -> 10
        # uint256 tokenAmount = msg.value.mul(tokenReserve).div(ethReserve).add(1); 1 * 10 / 0.5 + 1 = 21
        # uint256 liquidityCreated = msg.value.mul(totalLiquidity).div(ethReserve); 1 * 0.5 / 0.5 = 1
        # Would need 21 tokens, but specified max 15
    assert lgt.poolTotalSupply() == Wei("0.5 ether")
    assert lgt.balanceOf(accounts[1]) == 15


def test_add_liquidity_insufficient_liquidity(lgt, accounts):
    lgt.addLiquidity(0, 10, 99999999999, {'from': accounts[0], 'value': "0.5 ether"})
    lgt.mint(15, {'from': accounts[1]})

    with brownie.reverts('dev: not enough liquidity can be created'):
        tx = lgt.addLiquidity("1 ether", 15, 99999999999, {'from': accounts[1], 'value': "0.5 ether"})
        assert tx.return_value == 0
        # uint256 ethReserve = address(this).balance - msg.value;  -> 0.5 ether
        # uint256 tokenReserve = totalSupply() - ownedSupply(); -> 10
        # uint256 tokenAmount = msg.value.mul(tokenReserve).div(ethReserve).add(1); 0.5 * 10 / 0.5 + 1 = 11
        # uint256 liquidityCreated = msg.value.mul(totalLiquidity).div(ethReserve); 0.5 * 0.5 / 0.5 = 0.5
        # Would create 0.5 liquidity, bit minimum 1 is requested
    assert lgt.poolTotalSupply() == Wei("0.5 ether")
    assert lgt.balanceOf(accounts[1]) == 15
