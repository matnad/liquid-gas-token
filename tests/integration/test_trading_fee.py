from brownie import *
import pytest


DEADLINE = 999999999999


def test_fee(int_lgt, rpc, accounts):
    """ Test if fee structure of liquidity pool is working as intended. """
    # setup and verify liquidity shares
    provider = accounts[0]
    spender = accounts[4]
    provider_absolute_share = int_lgt.poolBalanceOf(provider)
    total_shares = int_lgt.poolTotalSupply()
    assert provider_absolute_share == "0.05 ether"
    assert total_shares == "0.1 ether"
    provider_share = provider_absolute_share / total_shares
    assert provider_share == 0.5
    initial_token_res = int_lgt.poolTokenReserves()
    initial_eth_res = int_lgt.balance()

    # Check how much tokens and ether we would get now
    rpc.snapshot()
    tx = int_lgt.removeLiquidity("0.05 ether", 1, 1, DEADLINE, {'from': provider})
    initial_withdraw = tx.return_value
    assert initial_withdraw == ("0.05 ether", 51)
    rpc.revert()

    # process some transactions
    int_lgt.buyAndFree(10, DEADLINE, spender, {'from': spender, 'value': "1 ether"})
    int_lgt.ethToTokenSwapOutput(30, DEADLINE, {'from': spender, 'value': "1 ether"})
    int_lgt.mintToSell(40, 1, DEADLINE, {'from': spender})
    # -> same amount of tokens in the exchange, but should have more eth
    assert initial_token_res == int_lgt.poolTokenReserves()
    assert initial_eth_res < int_lgt.balance()

    # Remove Liquidity and realize fee profits
    current_balance = int_lgt.balance()
    assert int_lgt.poolBalanceOf(provider) == "0.05 ether"
    tx = int_lgt.removeLiquidity("0.05 ether", 1, 1, DEADLINE, {'from': provider})
    eth_withdrawn, tokens_withdrawn = tx.return_value
    # assert the provider made a profit equal to his share
    assert tokens_withdrawn == 51
    assert eth_withdrawn > "0.05 ether"
    assert eth_withdrawn * 10 ** -18 == pytest.approx(current_balance * provider_share * 10 ** -18, abs=0.0001)
