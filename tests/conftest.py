#!/usr/bin/python3
import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass


@pytest.fixture(scope="module")
def lgt(LiquidGasToken, accounts):
    # lgt_deployer = accounts.add("0x7d4cbcfd42fe584226a17f385f734b046090f3e9d9fd95b2e10ef53acbbc39e2")
    lgt_deployer = accounts[-1]
    accounts[9].transfer(lgt_deployer, "1 ether")
    accounts[9].transfer("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c", "0.001 ether")
    lgt = lgt_deployer.deploy(LiquidGasToken)
    lgt.mint(30, {'from': accounts[0]})
    yield lgt
