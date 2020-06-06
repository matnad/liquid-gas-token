#!/usr/bin/python3

import pytest
from brownie import project


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(0, 50, 99999999999, {'from': accounts[0], 'value': "0.3 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity("0.25 ether", 50, 99999999999, {'from': accounts[1], 'value': "0.25 ether"})
    yield lgt


@pytest.fixture(scope="module")
def helper(LgtHelper, liquid_lgt, accounts):
    lgtHelper = accounts[0].deploy(LgtHelper)
    for a in accounts[:6]:
        liquid_lgt.approve(lgtHelper, 2**256-1, {'from': a})
    yield lgtHelper
