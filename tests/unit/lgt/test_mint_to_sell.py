import pytest
import brownie

DEADLINE = 99999999999


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.addLiquidity(1, 20, DEADLINE, {'from': accounts[0], 'value': "0.019 ether"})
    yield lgt


def test_mint_to_sell(liquid_lgt, accounts):
    initial_balance = accounts[4].balance()
    expected_eth_payout = liquid_lgt.getTokenToEthInputPrice(10)
    tx = liquid_lgt.mintToSell(10, 0, DEADLINE, {'from': accounts[4]})
    assert tx.return_value == expected_eth_payout
    assert accounts[4].balance() - initial_balance == expected_eth_payout
    assert liquid_lgt.ownedSupply() == 10
    assert liquid_lgt.poolTokenReserves() == 21 + 10


def test_mint_to_sell_to(liquid_lgt, accounts):
    initial_balance4 = accounts[4].balance()
    initial_balance5 = accounts[5].balance()
    expected_eth_payout = liquid_lgt.getTokenToEthInputPrice(20)
    tx = liquid_lgt.mintToSellTo(20, 0, DEADLINE, accounts[5], {'from': accounts[4]})
    assert tx.return_value == expected_eth_payout
    assert accounts[4].balance() == initial_balance4
    assert accounts[5].balance() - initial_balance5 == expected_eth_payout
    assert liquid_lgt.ownedSupply() == 10
    assert liquid_lgt.poolTokenReserves() == 21 + 20


def test_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.mintToSell(10, 0, 1, {'from': accounts[4]})


def test_no_tokens_sell_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must sell one or more tokens"):
        liquid_lgt.mintToSell(0, 0, DEADLINE, {'from': accounts[4]})


def test_insufficient_payout_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: tokens not worth enough"):
        eth_bought = liquid_lgt.getTokenToEthInputPrice(10)
        liquid_lgt.mintToSell(10, eth_bought + 1, DEADLINE, {'from': accounts[4]})


def test_to_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.mintToSellTo(10, 0, 1, accounts[5], {'from': accounts[4]})


def test_to_no_tokens_sell_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: must sell one or more tokens"):
        liquid_lgt.mintToSellTo(0, 0, DEADLINE, accounts[5], {'from': accounts[4]})


def test_to_insufficient_payout_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: tokens not worth enough"):
        eth_bought = liquid_lgt.getTokenToEthInputPrice(10)
        liquid_lgt.mintToSellTo(10, eth_bought + 1, DEADLINE, accounts[5], {'from': accounts[4]})