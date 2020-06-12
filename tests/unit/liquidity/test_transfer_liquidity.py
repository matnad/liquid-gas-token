import brownie
import pytest
from brownie import Wei

DEADLINE = 9999999999999
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture()
def liquid_lgt(lgt, accounts):
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(1, 51, 99999999999, {'from': accounts[0], 'value': "0.05 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[1], 'value': "0.049 ether"})
    yield lgt


def test_transfer_liquidity(liquid_lgt, accounts):
    sender, recipient = accounts[:2]
    sender_initial_liquidity = liquid_lgt.poolBalanceOf(sender)
    recipient_initial_liquidity = liquid_lgt.poolBalanceOf(recipient)
    transfer_amount = Wei("0.01 ether")
    tx = liquid_lgt.poolTransfer(recipient, transfer_amount, {'from': sender})
    assert tx.return_value
    event = tx.events['TransferLiquidity']
    assert event["from"] == sender
    assert event["to"] == recipient
    assert event["value"] == transfer_amount
    assert sender_initial_liquidity - transfer_amount == liquid_lgt.poolBalanceOf(sender)
    assert recipient_initial_liquidity + transfer_amount == liquid_lgt.poolBalanceOf(recipient)


def test_transfer_liquidity_insufficient_reverts(liquid_lgt, accounts):
    sender, recipient = accounts[:2]
    sender_initial_liquidity = liquid_lgt.poolBalanceOf(sender)
    recipient_initial_liquidity = liquid_lgt.poolBalanceOf(recipient)
    transfer_amount = Wei("1 ether")
    with brownie.reverts("LGT: transfer exceeds balance"):
        liquid_lgt.poolTransfer(recipient, transfer_amount, {'from': sender})
    assert sender_initial_liquidity == liquid_lgt.poolBalanceOf(sender)
    assert recipient_initial_liquidity == liquid_lgt.poolBalanceOf(recipient)


def test_transfer_liquidity_self_reverts(liquid_lgt, accounts):
    sender = accounts[0]
    sender_initial_liquidity = liquid_lgt.poolBalanceOf(sender)
    recipient_initial_liquidity = liquid_lgt.poolBalanceOf(liquid_lgt)
    transfer_amount = Wei("0.001 ether")
    with brownie.reverts("dev: can't transfer liquidity to token contract"):
        liquid_lgt.poolTransfer(liquid_lgt, transfer_amount, {'from': sender})
    assert sender_initial_liquidity == liquid_lgt.poolBalanceOf(sender)
    assert recipient_initial_liquidity == liquid_lgt.poolBalanceOf(liquid_lgt)


def test_transfer_liquidity_zero_reverts(liquid_lgt, accounts):
    sender = accounts[0]
    recipient = ZERO_ADDRESS
    sender_initial_liquidity = liquid_lgt.poolBalanceOf(sender)
    recipient_initial_liquidity = liquid_lgt.poolBalanceOf(ZERO_ADDRESS)
    transfer_amount = Wei("0.005 ether")
    with brownie.reverts("dev: can't transfer liquidity to zero address"):
        liquid_lgt.poolTransfer(recipient, transfer_amount, {'from': sender})
    assert sender_initial_liquidity == liquid_lgt.poolBalanceOf(sender)
    assert recipient_initial_liquidity == liquid_lgt.poolBalanceOf(recipient)
