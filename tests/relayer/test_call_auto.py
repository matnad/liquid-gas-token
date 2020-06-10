DEADLINE = 99999999999


def test_forward_auto_no_gas_cost_refund(liquid_lgt, relayer, helper, accounts):
    """
    Burn 1 million gas, expected to buy 25 tokens if gas price is high enough
    Gas cost is 0, so no purchase will happen, but the ether should be refunded.
    """
    initial_tokens = liquid_lgt.poolTokenReserves()
    initial_balance = accounts[0].balance()
    expected_eth_sold = liquid_lgt.getEthToTokenOutputPrice(25)
    calldata = "0x4ad5d16f00000000000000000000000000000000000000000000000000000000000f4240"
    tx = relayer.forwardAuto(helper, 0, calldata, {'from': accounts[0], 'value': "1 ether"})
    assert tx.return_value == (25, expected_eth_sold)
    assert tx.gas_price == 0
    assert tx.gas_used > 1e6
    assert initial_tokens == liquid_lgt.poolTokenReserves()
    assert initial_balance == accounts[0].balance()
