import pytest
import brownie


@pytest.fixture()
def liquidLgt(lgt, accounts):
    lgt.addLiquidity(0, 20, 99999999999, {'from': accounts[0], 'value': "0.1 ether"})
    yield lgt


def test_mint_to_sell(liquidLgt, accounts):
    initial_balance = accounts[4].balance()
    eth_bought = liquidLgt.getTokenToEthInputPrice(10)
    tx = liquidLgt.mintToSell(10, 0, 99999999999999, {'from': accounts[4]})
    assert tx.return_value == eth_bought
    assert accounts[4].balance() - initial_balance == tx.return_value
    assert liquidLgt.ownedSupply() == 10
    assert liquidLgt.totalSupply() == 40


def test_mint_to_sell_to(liquidLgt, accounts):
    initial_balance4 = accounts[4].balance()
    initial_balance5 = accounts[5].balance()
    eth_bought = liquidLgt.getTokenToEthInputPrice(20)
    tx = liquidLgt.mintToSellTo(20, 0, 99999999999999, accounts[5], {'from': accounts[4]})
    assert tx.return_value == eth_bought
    assert accounts[4].balance() == initial_balance4
    assert accounts[5].balance() - initial_balance5 == tx.return_value
    assert liquidLgt.ownedSupply() == 10
    assert liquidLgt.totalSupply() == 50


def test_mint_to_sell_reverts(liquidLgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquidLgt.mintToSell(10, 0, 1, {'from': accounts[4]})
    with brownie.reverts("dev: must sell one or more tokens"):
        liquidLgt.mintToSell(0, 0, 99999999999999, {'from': accounts[4]})
    with brownie.reverts("dev: tokens not worth enough"):
        eth_bought = liquidLgt.getTokenToEthInputPrice(10)
        liquidLgt.mintToSell(10, eth_bought + 1, 99999999999999, {'from': accounts[4]})
    with brownie.reverts("dev: can't send to liquid token contract"):
        liquidLgt.mintToSellTo(10, 0, 99999999999999, liquidLgt.address, {'from': accounts[4]})
    with brownie.reverts("dev: can't send to zero address"):
        liquidLgt.mintToSellTo(10, 0, 99999999999999, "0x0000000000000000000000000000000000000000", {'from': accounts[4]})
