from brownie import *

from archive.deploy_lgt import deploy_lgt


def main():
    """Deploys a funded and approved LGT."""
    lgt = deploy_lgt()

    helper = accounts[0].deploy(LgtHelper)

    for i in range(2):
        lgt.approve(helper, 2**256-1, {'from': accounts[i]})

    return lgt, helper, accounts[1]
# lgt, h, me = run("lgt")