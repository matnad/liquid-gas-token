from brownie import *

from scripts.deploy_lgt import deploy_lgt


def main():
    """Deploys a funded and approved LGT."""
    lgt = deploy_lgt()
    lgt.mint(180, {'from': accounts[0]})
    lgt.addLiquidity(0, 150, 99999999999, {'from': accounts[0], 'value': "1.1 ether"})
    lgt.mint(120, {'from': accounts[1]})
    lgt.addLiquidity("0.5 ether", 100, 99999999999, {'from': accounts[1], 'value': "0.5 ether"})

    helper = accounts[0].deploy(LgtHelper)

    for i in range(5):
        lgt.approve(helper, 2**256-1, {'from': accounts[i]})

    return lgt, helper, accounts[1]
# lgt, h, me = run("lgt")