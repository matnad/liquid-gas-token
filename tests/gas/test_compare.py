import pytest
from brownie import *

BURN = 1e6
FREE = 25


def test_funded(liquid_lgt, helper, accounts):
    """Verify correct deployment of liquid_lgt fixture and LgtHelper"""
    assert liquid_lgt.poolTotalSupply() == "1.6 ether"
    assert liquid_lgt.totalSupply() - liquid_lgt.ownedSupply() == 219
    assert liquid_lgt.balanceOf(accounts[0]) == 30
    assert liquid_lgt.balanceOf(accounts[1]) == 51
    assert liquid_lgt.ownedSupply() == 81
    assert liquid_lgt.totalSupply() == 300

    tx = helper.burnGas(BURN, {'from': accounts[3]})
    assert tx.gas_used > BURN


def test_uniswap_gst(helper, uniswap_gst, gst2, accounts):
    assert gst2.balanceOf(accounts[0]) == 50
    price = uniswap_gst.getEthToTokenOutputPrice(FREE)
    # print("Uniswap Price:", price)
    tx_buy = uniswap_gst.ethToTokenSwapOutput(FREE, 9999999999, {'from': accounts[0], 'value': price})
    buy_gas = tx_buy.gas_used
    tx_use = helper.burnAndFreeGST(BURN, FREE)
    burn_gas = tx_use.gas_used
    # print("Buy Gas:", buy_gas, " Burn Gas:", burn_gas, " Total Gas:", buy_gas + burn_gas)
    print("UNI + GST Gas:", buy_gas + burn_gas, "( buy:", buy_gas, ", burn:", burn_gas, ")")


def test_gst(helper, gst2, accounts):
    assert gst2.balanceOf(accounts[0]) == 50
    tx = helper.burnAndFreeGST(BURN, FREE)
    tx.call_trace()
    print("GST Gas:", tx.gas_used)


def test_uniswap_chi(helper, uniswap_chi, chi, accounts):
    assert chi.balanceOf(accounts[0]) == 50
    assert chi.balanceOf(uniswap_chi) >= 40
    price = uniswap_chi.getEthToTokenOutputPrice(FREE)
    # print("Uniswap Price:", price)
    tx_buy = uniswap_chi.ethToTokenSwapOutput(FREE, 9999999999, {'from': accounts[0], 'value': price})
    buy_gas = tx_buy.gas_used
    tx_use = helper.burnAndFreeCHI(BURN, FREE)
    burn_gas = tx_use.gas_used
    print("UNI + GST Gas:", buy_gas + burn_gas, "( buy:", buy_gas, ", burn:", burn_gas, ")")


def test_chi(helper, chi, accounts):
    assert chi.balanceOf(accounts[0]) == 50
    tx = helper.burnAndFreeCHI(BURN, FREE)
    tx.call_trace()
    print("CHI Gas:", tx.gas_used)


def test_lgt(helper, liquid_lgt, accounts):
    price = liquid_lgt.getEthToTokenOutputPrice(FREE)
    tx_free = helper.burnBuyAndFree(BURN, FREE, {'from': accounts[1], 'value': price})
    tx_free.call_trace()
    print("LGT Gas:", tx_free.gas_used)
