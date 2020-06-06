import brownie
import pytest


def test_balance(lgt, accounts):
    assert lgt.balanceOf(accounts[0]) == 30


def test_approve(lgt, accounts):
    lgt.approve(accounts[1], 50, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 50
    assert lgt.allowance(accounts[0], accounts[2]) == 0

    lgt.approve(accounts[1], 60, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 60


def test_increase_approval(lgt, accounts):
    lgt.approve(accounts[1], 20, {'from': accounts[0]})
    lgt.increaseAllowance(accounts[1], 10, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 30


def test_increase_approval_reverts(lgt, accounts):
    lgt.approve(accounts[1], 30, {'from': accounts[0]})
    with brownie.reverts("SafeMath: addition overflow"):
        lgt.increaseAllowance(accounts[1], 2**256-1, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 30


def test_decrease_approval(lgt, accounts):
    lgt.approve(accounts[1], 40, {'from': accounts[0]})
    lgt.decreaseAllowance(accounts[1], 5, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 35


def test_decrease_approval_reverts(lgt, accounts):
    lgt.approve(accounts[1], 50, {'from': accounts[0]})
    with brownie.reverts("ERC20: decreased allowance below zero"):
        lgt.decreaseAllowance(accounts[1], 60, {'from': accounts[0]})
    assert lgt.allowance(accounts[0], accounts[1]) == 50


def test_transfer_from(lgt, accounts):
    """Transfer lgts with transferFrom"""
    lgt.approve(accounts[1], 15, {'from': accounts[0]})
    lgt.transferFrom(accounts[0], accounts[2], 5, {'from': accounts[1]})

    assert lgt.balanceOf(accounts[2]) == 5
    assert lgt.balanceOf(accounts[1]) == 0
    assert lgt.balanceOf(accounts[0]) == 25
    assert lgt.allowance(accounts[0], accounts[1]) == 10


@pytest.mark.parametrize('idx', [0, 1, 2])
def test_transfer_from_reverts(lgt, accounts, idx):
    """transerFrom should revert"""
    with brownie.reverts("ERC20: transfer amount exceeds allowance"):
        lgt.transferFrom(accounts[0], accounts[2], 20, {'from': accounts[idx]})
