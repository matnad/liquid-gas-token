#!/usr/bin/python3
import os

from brownie import *


def deploy_lgt():
    """Deploys LGT at a 15 byte address."""
    rpc.reset()

    lgt_deployer_pk = os.getenv("LGT_DEPLOYER")
    if lgt_deployer_pk:
        lgt_deployer = accounts.add(lgt_deployer_pk)
    else:
        lgt_deployer = accounts.load("gst_deployer")

    accounts[9].transfer(lgt_deployer, "20 ether")
    accounts[9].transfer("0x00000000007475142d6329FC42Dc9684c9bE6cD0", "0.001 ether")
    nonce = 69
    lgt = None
    for i in range(nonce + 1):
        if i == nonce:
            lgt = lgt_deployer.deploy(LiquidGasToken)
        else:
            lgt_deployer.transfer(accounts[0], "0", silent=True)

    return lgt


def main():
    return deploy_lgt()

# lgt = run("deploy_lgt")