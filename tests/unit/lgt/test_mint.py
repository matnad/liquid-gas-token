def test_mint(lgt, accounts):
    initial_tokens = lgt.balanceOf(accounts[5])
    lgt.mint(10, {'from': accounts[5]})
    assert initial_tokens + 10 == lgt.balanceOf(accounts[5])


def test_mint_for(lgt, accounts):
    initial_tokens5 = lgt.balanceOf(accounts[5])
    initial_tokens6 = lgt.balanceOf(accounts[6])
    lgt.mintFor(10, accounts[6], {'from': accounts[5]})
    assert initial_tokens5 == lgt.balanceOf(accounts[5])
    assert initial_tokens6 + 10 == lgt.balanceOf(accounts[6])
