from brownie import *

from scripts.deploy_lgt import deploy_lgt


def main():
    """
    Deploys, funds and approves GST2, CHI and LGT.
    Must be run on mainnet fork.
    """

    # Deploy and fund LGT
    lgt = deploy_lgt()
    lgt.mint(180, {'from': accounts[0]})
    lgt.addLiquidity(0, 150, 99999999999, {'from': accounts[0], 'value': "1.1 ether"})
    lgt.mint(120, {'from': accounts[1]})
    lgt.addLiquidity("0.5 ether", 100, 99999999999, {'from': accounts[1], 'value': "0.5 ether"})
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