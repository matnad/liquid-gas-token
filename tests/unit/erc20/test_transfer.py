#!/usr/bin/python3
import brownie


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_transfer(lgt, accounts):
    assert lgt.balanceOf(accounts[0]) == 30
    lgt.transfer(accounts[1], 10, {'from': accounts[0]})
    assert lgt.balanceOf(accounts[1]) == 10
    assert lgt.balanceOf(accounts[0]) == 20


def test_transfer_exceed_reverts(lgt, accounts):
    with brownie.reverts("ERC20: transfer exceeds balance"):
        lgt.transfer(accounts[1], 10, {'from': accounts[2]})


def test_transfer_zero_reverts(lgt, accounts):
    with brownie.reverts("ERC20: transfer to zero address"):
        lgt.transfer(ZERO_ADDRESS, 10, {'from': accounts[0]})
