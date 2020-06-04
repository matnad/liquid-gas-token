import pytest
from brownie import *

BURN = 1e6
FREE = 25


def calculate_refund(tokenAmount: int) -> "Wei":
    cost_free = Wei(14154) + tokenAmount * 6870
    refund = Wei(24000) * tokenAmount
    return (cost_free - refund) * -1


def test_funded(liquid_lgt, helper, accounts):
    """Verify correct deployment of liquid_lgt fixture and LgtHelper"""
    assert liquid_lgt.poolTotalSupply() == "1.6 ether"
    assert liquid_lgt.totalSupply() - liquid_lgt.ownedSupply() == 219
    assert liquid_lgt.balanceOf(accounts[0]) == 30
    assert liquid_lgt.balanceOf(accounts[1]) == 51
    assert liquid_lgt.ownedSupply() == 81
    assert liquid_lgt.totalSupply() == 300

    assert helper.LGT() == liquid_lgt.address
    tx = helper.burnGas(BURN, {'from': accounts[3]})
    assert tx.gas_used > BURN


def test_free_from(liquid_lgt, helper, accounts):
    free = FREE
    tx_burn = helper.burnGas(BURN, {'from': accounts[1]})
    tx_free = helper.burnAndFree(BURN, free, {'from': accounts[1]})
    expected_refund = calculate_refund(free)
    max_overhead = 20000
    assert tx_burn.gas_used == pytest.approx(tx_free.gas_used + expected_refund, max_overhead)
    print(tx_burn.gas_used, tx_free.gas_used + expected_refund, tx_free.gas_used, expected_refund)
    print("Overhead:", tx_free.gas_used + expected_refund - tx_burn.gas_used)


def test_buy_and_free(liquid_lgt, helper, accounts):
    free = FREE
    initial_balance = accounts[1].balance()
    tx_burn = helper.burnGas(BURN, {'from': accounts[1]})
    eth_sold = liquid_lgt.getEthToTokenOutputPrice(free)
    tx_free = helper.burnBuyAndFree(BURN, free, {'from': accounts[1], 'value': "2 ether"})
    expected_refund = calculate_refund(free)
    max_overhead = 20000
    assert tx_free.return_value == eth_sold
    assert initial_balance - eth_sold == accounts[1].balance()
    assert tx_burn.gas_used == pytest.approx(tx_free.gas_used + expected_refund, max_overhead)
    print(tx_burn.gas_used, tx_free.gas_used + expected_refund, tx_free.gas_used, expected_refund)
    print("Overhead:", tx_free.gas_used + expected_refund - tx_burn.gas_used)


def test_buy_and_free_exact(liquid_lgt, helper, accounts):
    free = FREE
    initial_balance = accounts[1].balance()
    tx_burn = helper.burnGas(BURN, {'from': accounts[1]})
    eth_sold = liquid_lgt.getEthToTokenOutputPrice(free)
    tx_free = helper.burnBuyAndFree(BURN, free, {'from': accounts[1], 'value': eth_sold})
    expected_refund = calculate_refund(free)
    max_overhead = 20000
    assert tx_free.return_value == eth_sold
    assert initial_balance - eth_sold == accounts[1].balance()
    assert tx_burn.gas_used == pytest.approx(tx_free.gas_used + expected_refund, max_overhead)
    print(tx_burn.gas_used, tx_free.gas_used + expected_refund, tx_free.gas_used, expected_refund)
    print("Overhead:", tx_free.gas_used + expected_refund - tx_burn.gas_used)


def test_buy_up_to_and_free(liquid_lgt, helper, accounts):
    free = FREE
    initial_balance = accounts[1].balance()
    tx_burn = helper.burnGas(BURN, {'from': accounts[1]})
    eth_sold = liquid_lgt.getEthToTokenOutputPrice(free)
    tx_free = helper.burnBuyUpToAndFree(BURN, free, {'from': accounts[1], 'value': "2 ether"})
    expected_refund = calculate_refund(free)
    max_overhead = 20000
    assert tx_free.return_value == free
    # assert initial_balance - eth_sold == accounts[1].balance()
    assert tx_burn.gas_used == pytest.approx(tx_free.gas_used + expected_refund, max_overhead)
    print(tx_burn.gas_used, tx_free.gas_used + expected_refund, tx_free.gas_used, expected_refund)
    print("Overhead:", tx_free.gas_used + expected_refund - tx_burn.gas_used)

