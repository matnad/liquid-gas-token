"""
These tests don't verify if gas is refunded, only if tokens are burned.
This is done with integration tests.
"""


def test_free(lgt, accounts):
    assert lgt.balanceOf(accounts[0]) == 30
    tx = lgt.free(10, {'from': accounts[0]})
    assert tx.return_value
    assert lgt.balanceOf(accounts[0]) == 20


def test_free_zero(lgt, accounts):
    assert lgt.balanceOf(accounts[0]) == 30
    tx = lgt.free(0, {'from': accounts[0]})
    assert tx.return_value
    assert lgt.balanceOf(accounts[0]) == 30


def test_free_from(lgt, accounts):
    owner, spender = accounts[:2]
    assert lgt.balanceOf(owner) == 30
    lgt.approve(spender, 11, {'from': owner})
    assert lgt.allowance(owner, spender) == 11
    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert tx.return_value
    assert lgt.balanceOf(owner) == 20
    assert lgt.allowance(owner, spender) == 1


def test_free_from_zero(lgt, accounts):
    owner, spender = accounts[:2]
    assert lgt.balanceOf(owner) == 30
    lgt.approve(spender, 11, {'from': owner})
    assert lgt.allowance(owner, spender) == 11
    tx = lgt.freeFrom(0, owner, {'from': spender})
    assert tx.return_value
    assert lgt.balanceOf(owner) == 30
    assert lgt.allowance(owner, spender) == 11


def test_no_spender_balance_fails(lgt, accounts):
    owner, spender = accounts[:2]
    tx = lgt.free(10, {'from': spender})
    assert not tx.return_value


def test_no_allowance_fails(lgt, accounts):
    owner, spender = accounts[:2]
    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert not tx.return_value


def test_insufficient_allowance_fails(lgt, accounts):
    owner, spender = accounts[:2]
    lgt.approve(spender, 5, {'from': owner})
    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert not tx.return_value


def test_insufficient_owner_balance_fails(lgt, accounts):
    owner, spender = accounts[:2]
    lgt.approve(spender, 100, {'from': owner})
    tx = lgt.freeFrom(50, owner, {'from': spender})
    assert not tx.return_value
