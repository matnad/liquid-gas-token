from brownie import *

from scripts.deploy_lgt import deploy_lgt


def main():
    """
    Deploys, funds and approves GST2, CHI and LGT.
    Must be run on mainnet fork.
    """
    rpc.reset()
    # Deploy and fund LGT
    lgt_deployer = accounts.add("0x7d4cbcfd42fe584226a17f385f734b046090f3e9d9fd95b2e10ef53acbbc39e2")
    accounts[9].transfer("0x000000000049091f98692b2460500b6d133ae31f", "0.001 ether")

    lgt = lgt_deployer.deploy(LiquidGasToken)
    lgt.mint(80, {'from': accounts[0]})
    lgt.addLiquidity(1, 50, 999999999999999, {'from': accounts[0], 'value': "0.049 ether"})
    lgt.mint(70, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 999999999999999, {'from': accounts[1], 'value': "0.049 ether"})
    lgt.mint(50, {'from': accounts[2]})

    # Load GST2
    gst = interface.IGST("0x0000000000b3F879cb30FE243b4Dfee438691c04")
    gst.mint(30, {'from': accounts[0]})
    gst.mint(20, {'from': accounts[1]})
    gst.mint(50, {'from': accounts[2]})

    # Load CHI
    chi = interface.ICHI("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c")
    # chi = Contract.from_explorer("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c")
    chi.mint(30, {'from': accounts[0]})
    chi.mint(20, {'from': accounts[1]})
    chi.mint(50, {'from': accounts[2]})

    # deploy helper contract and approve it
    helper = accounts[0].deploy(LgtHelper)
    for i in range(5):
        lgt.approve(helper, 2**256-1, {'from': accounts[i]})
        gst.approve(helper, 2 ** 256 - 1, {'from': accounts[i]})
        chi.approve(helper, 2 ** 256 - 1, {'from': accounts[i]})

    return lgt, gst, chi, helper, accounts[2]
# lgt, gst, chi, h, me = run("all_gts")