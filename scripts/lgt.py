from brownie import *

from scripts.deploy_lgt import deploy_lgt


def main():
    """Deploys a funded and approved LGT."""
    lgt = deploy_lgt()
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[0], 'value': "0.049 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[1], 'value': "0.049 ether"})

    helper = accounts[0].deploy(LgtHelper)

    for i in range(3):
        lgt.approve(helper, 2**256-1, {'from': accounts[i]})

    return lgt, helper, accounts[1]
# lgt, h, me = run("lgt")