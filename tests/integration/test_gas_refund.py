from brownie import *


DEADLINE = 999999999999


def test_gas_refund(helper, accounts):
    """ Test if a gas reduction is achieved by burning tokens """
    tx = helper.burnBuyAndFree(1000000, 25, {'from': accounts[0], 'value': "1 ether"})
    assert tx.gas_used < 700000
