# import pytest
# from brownie import *


def test_deploy_lgt(lgt):
    assert lgt.name() == "Liquid Gas Token"
    assert lgt.symbol() == "LGT"
    assert lgt.decimals() == 0


def test_mint_lgt(lgt, accounts):
    lgt.mint(1, {'from': accounts[1]})
    lgt.mint(2, {'from': accounts[2]})
    assert lgt.balanceOf(accounts[1]) == 1
    assert lgt.balanceOf(accounts[2]) == 2
    assert lgt.totalSupply() == 33
