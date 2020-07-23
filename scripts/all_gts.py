from brownie import *


def main():
    """
    Deploys, funds and approves GST2, CHI and LGT.
    Must be run on mainnet fork.
    """
    rpc.reset()
    # Deploy and fund LGT
    salt = "0x23ad710e5baee63bb004d962a84d3922e236c107944f2efe53e42d51e6d6f121"
    coffee = accounts.add("redacted")
    accounts[0].transfer(coffee, "1 ether")
    d = coffee.deploy(LGTDeployer)  # 0x8EE26bA26c87Beb287eB71245ADEf44ede1bF190
    coffee.transfer("0x000000000000C1CB11D5c062901F32D06248CE48", "0.001 ether")
    d.deploy(salt)
    lgt = LiquidGasToken.at("0x000000000000C1CB11D5c062901F32D06248CE48")
    lgt.mint(110, {'from': accounts[0]})
    lgt.addLiquidity(1, 50, 999999999999999, {'from': accounts[0], 'value': "0.049 ether"})
    lgt.mint(70, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 999999999999999, {'from': accounts[1], 'value': "0.049 ether"})
    lgt.mint(50, {'from': accounts[2]})

    # Load GST2
    gst = interface.IGST("0x0000000000b3F879cb30FE243b4Dfee438691c04")
    gst.mint(60, {'from': accounts[0]})
    gst.mint(20, {'from': accounts[1]})
    gst.mint(50, {'from': accounts[2]})

    # Load CHI
    chi = interface.ICHI("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c")
    # chi = Contract.from_explorer("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c")
    chi.mint(60, {'from': accounts[0]})
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