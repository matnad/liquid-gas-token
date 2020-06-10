DEADLINE = 99999999999


def test_call_max_no_value(liquid_lgt, relayer, storage, accounts):
    initial_tokens = liquid_lgt.poolTokenReserves()
    calldata = "60fe47b1000000000000000000000000000000000000000000000000000000000000000f"
    expected_tokens = liquid_lgt.getEthToTokenInputPrice("0.003 ether")
    assert expected_tokens > 0
    tx = relayer.forwardMax(DEADLINE, storage, 0, calldata, {'from': accounts[0], 'value': "0.003 ether"})
    assert tx.return_value == expected_tokens
    assert storage.get() == "0xf"
    assert initial_tokens - expected_tokens == liquid_lgt.poolTokenReserves()


def test_call_max_with_value(liquid_lgt, relayer, storage, accounts):
    """ Buy tokens for 0.004 ether and send 0.002 ether with the call. """
    initial_tokens = liquid_lgt.poolTokenReserves()
    calldata = "bc25bd200000000000000000000000000000000000000000000000000000000000000000"
    expected_tokens = liquid_lgt.getEthToTokenInputPrice("0.004 ether")
    assert expected_tokens > 0
    tx = relayer.forwardMax(DEADLINE, storage, "0.002 ether", calldata, {'from': accounts[0], 'value': "0.006 ether"})
    assert tx.return_value == expected_tokens
    assert storage.get() == "0.002 ether"
    assert initial_tokens - expected_tokens == liquid_lgt.poolTokenReserves()
