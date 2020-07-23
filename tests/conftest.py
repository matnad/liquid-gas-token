#!/usr/bin/python3
import os

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass


@pytest.fixture(scope="module")
def lgt(LiquidGasToken, LGTDeployer, accounts):
    salt = "0x23ad710e5baee63bb004d962a84d3922e236c107944f2efe53e42d51e6d6f121"
    coffee = accounts.add("redacted")
    d = coffee.deploy(LGTDeployer)  # 0x8EE26bA26c87Beb287eB71245ADEf44ede1bF190
    accounts[0].transfer("0x000000000000C1CB11D5c062901F32D06248CE48", "0.001 ether")
    d.deploy(salt)
    lgt = LiquidGasToken.at("0x000000000000C1CB11D5c062901F32D06248CE48")
    lgt.mint(30, {'from': accounts[0]})
    yield lgt
