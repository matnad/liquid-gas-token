from brownie import *

from scripts.deploy_lgt import deploy_lgt


def main():
    lgt = deploy_lgt()
    for _ in range(6):
        lgt.mint(100, {'from': accounts[1]})
    lgt.addLiquidity(0, 500, 99999999999, {'from': accounts[1], 'value': "0.1 ether"})
    lgt.transfer(accounts[0], 10, {'from': accounts[1]})

    helper = TestModifier.deploy({'from': accounts[1]})


    return lgt, helper, accounts[0]

# lgt, h, me = run("modifier")