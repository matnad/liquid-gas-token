#!/usr/bin/python3
import os

from brownie import *


def deploy_lgt():
    """Deploys LGT at a 15 byte address."""
    rpc.reset()
    lgt_deployer = accounts.add("0x7d4cbcfd42fe584226a17f385f734b046090f3e9d9fd95b2e10ef53acbbc39e2")
    accounts[9].transfer("0x000000000049091f98692b2460500b6d133ae31f", "0.001 ether")
    lgt = lgt_deployer.deploy(LiquidGasToken)
    return lgt


def main():
    return deploy_lgt()

# lgt = run("deploy_lgt")