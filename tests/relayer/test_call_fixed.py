from brownie import Wei

DEADLINE = 99999999999


def test_forward_no_value_refund(liquid_lgt, relayer, storage, accounts):
    initial_tokens = liquid_lgt.poolTokenReserves()
    initial_balance = accounts[0].balance()
    calldata = "60fe47b1000000000000000000000000000000000000000000000000000000000000000e"
    expected_eth_sold = liquid_lgt.getEthToTokenOutputPrice(4)
    tx = relayer.forward(4, DEADLINE, storage, 0, calldata, {'from': accounts[0], 'value': "1 ether"})
    assert tx.return_value == expected_eth_sold
    assert storage.get() == "0xe"
    assert initial_tokens - 4 == liquid_lgt.poolTokenReserves()
    assert initial_balance - expected_eth_sold == accounts[0].balance()


def test_forward_no_value_exact(liquid_lgt, relayer, storage, accounts):
    initial_tokens = liquid_lgt.poolTokenReserves()
    initial_balance = accounts[0].balance()
    calldata = "60fe47b10000000000000000000000000000000000000000000000000000000000000001"
    expected_eth_sold = liquid_lgt.getEthToTokenOutputPrice(3)
    tx = relayer.forward(3, DEADLINE, storage, 0, calldata, {'from': accounts[0], 'value': expected_eth_sold})
    assert tx.return_value == expected_eth_sold
    assert storage.get() == "0x1"
    assert initial_tokens - 3 == liquid_lgt.poolTokenReserves()
    assert initial_balance - expected_eth_sold == accounts[0].balance()


def test_forward_with_value_refund(liquid_lgt, relayer, storage, accounts):
    """ send 0.01 ether with the call and buy 2 tokens """
    initial_tokens = liquid_lgt.poolTokenReserves()
    initial_balance = accounts[0].balance()
    calldata = "bc25bd200000000000000000000000000000000000000000000000000000000000000000"
    expected_eth_sold = liquid_lgt.getEthToTokenOutputPrice(2)
    tx = relayer.forward(2, DEADLINE, storage, "0.01 ether", calldata, {'from': accounts[0], 'value': "1 ether"})
    assert tx.return_value == expected_eth_sold
    assert storage.get() == "0.01 ether"
    assert initial_tokens - 2 == liquid_lgt.poolTokenReserves()
    assert initial_balance - expected_eth_sold - "0.01 ether" == accounts[0].balance()


def test_forward_with_value_exact(liquid_lgt, relayer, storage, accounts):
    """ send 0.2 ether with the call and buy 2 tokens """
    initial_tokens = liquid_lgt.poolTokenReserves()
    initial_balance = accounts[0].balance()
    calldata = "bc25bd200000000000000000000000000000000000000000000000000000000000000000"
    expected_eth_sold = liquid_lgt.getEthToTokenOutputPrice(6)
    total_ether = Wei(expected_eth_sold + "0.2 ether")
    tx = relayer.forward(6, DEADLINE, storage, "0.2 ether", calldata, {'from': accounts[0], 'value': total_ether})
    assert tx.return_value == expected_eth_sold
    assert storage.get() == "0.2 ether"
    assert initial_tokens - 6 == liquid_lgt.poolTokenReserves()
    assert initial_balance - total_ether == accounts[0].balance()
