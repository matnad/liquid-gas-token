#!/usr/bin/python3
import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass


@pytest.fixture(scope="module")
def lgt(LiquidGasToken, accounts):
    lgt_deployer_pk = os.getenv("LGT_DEPLOYER")
    if lgt_deployer_pk:
        lgt_deployer = accounts.add(lgt_deployer_pk)
    else:
        lgt_deployer = accounts.load("gst_deployer")
    assert lgt_deployer.nonce == 0
    accounts[9].transfer(lgt_deployer, "20 ether")
    accounts[9].transfer("0x00000000007475142d6329FC42Dc9684c9bE6cD0", "0.001 ether")
    nonce = 69
    lgt = None
    for i in range(nonce + 1):
        if i == nonce:
            lgt = LiquidGasToken.deploy({'from': lgt_deployer})
        else:
            lgt_deployer.transfer(accounts[0], "0", silent=True)
    lgt.mint(30, {'from': accounts[0]})
    yield lgt
