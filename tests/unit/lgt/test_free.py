def test_free(lgt, accounts):
    tx = lgt.free(10, {'from': accounts[0]})
    assert tx.return_value
    assert lgt.balanceOf(accounts[0]) == 20
    assert lgt.totalSupply() == 20


def test_free_from(lgt, accounts):
    owner, spender = accounts[:2]
    lgt.approve(spender, 11, {'from': owner})
    assert lgt.allowance(owner, spender) == 11
    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert tx.return_value
    assert lgt.balanceOf(owner) == 20
    assert lgt.totalSupply() == 20
    assert lgt.allowance(owner, spender) == 1


def test_free_fails(lgt, accounts):
    owner, spender = accounts[:2]

    tx = lgt.free(10, {'from': spender})
    assert not tx.return_value

    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert not tx.return_value

    lgt.approve(spender, 5, {'from': owner})
    tx = lgt.freeFrom(10, owner, {'from': spender})
    assert not tx.return_value

    lgt.approve(spender, 100, {'from': owner})
    tx = lgt.freeFrom(50, owner, {'from': spender})
    assert not tx.return_value
