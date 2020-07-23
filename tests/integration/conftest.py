import pytest


@pytest.fixture(scope="module")
def int_lgt(lgt, accounts):
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(1, 51, 99999999999, {'from': accounts[0], 'value': "0.05 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[1], 'value': "0.049 ether"})
    yield lgt


@pytest.fixture(scope="module")
def helper(int_lgt, accounts, LgtHelper):
    helper = accounts[0].deploy(LgtHelper)
    for i in range(3):
        int_lgt.approve(helper, 2**256-1, {'from': accounts[i]})
    yield helper
