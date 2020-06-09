from brownie import *

from brownie.utils import color
from scripts.all_gts import main as get_all_gas_tokens

TOKENS_MINT = 4
TOKENS_FREE = 25
BURN = 1000000
DEADLINE = 999999999999


def main():
    rpc.reset()
    # get gas token contracts
    lgt, gst, chi, h, me = get_all_gas_tokens()

    # get uniswap exchanges (and fund them)
    gst_uniswap = interface.UniswapExchangeInterface("0x929507CD3D90Ab11eC4822E9eB5A48eb3a178F19")
    gst.approve(gst_uniswap, 2 ** 256 - 1, {'from': accounts[0]})
    chi.mint(150, {'from': accounts[9]})
    chi_uniswap = interface.UniswapExchangeInterface("0xD772f5ac5c4145f3B2b460515d277f667253E6Dc")
    chi.approve(chi_uniswap, 2 ** 256 - 1, {'from': accounts[0]})
    chi.approve(chi_uniswap, 2 ** 256 - 1, {'from': accounts[9]})
    chi_uniswap.addLiquidity(1, 150, 99999999999, {'from': accounts[9], 'value': "0.04 ether"})
    rpc.snapshot()
    out = "Comparing Liquid Gas Token, CHI and GST2...\n"

    # Minting
    out += f"\n  Minting {TOKENS_MINT} tokens:\n"

    tx = gst.mint(TOKENS_MINT, {'from': accounts[0]})
    out += f"       {color('dark green')}GST2: {str(tx.gas_used).ljust(6)} gas (mint to balance){color}\n"
    tx = chi.mint(TOKENS_MINT, {'from': accounts[0]})
    out += f"        CHI: {str(tx.gas_used).ljust(6)} gas (mint to balance)\n"
    tx = lgt.mint(TOKENS_MINT, {'from': accounts[0]})
    out += f"        LGT: {str(tx.gas_used).ljust(6)} gas (mint to balance)\n"
    rpc.revert()

    # Minting and selling
    out += f"\n  Minting {TOKENS_MINT} tokens and selling them on Uniswap:\n"

    tx_mint = gst.mint(TOKENS_MINT, {'from': accounts[0]})
    tx_sell = gst_uniswap.tokenToEthSwapInput(TOKENS_MINT, 1, 9999999999, {'from': accounts[0]})
    out += f"       GST2: {str(tx_mint.gas_used + tx_sell.gas_used).ljust(6)} gas (mint and sell)\n"

    tx_mint = chi.mint(TOKENS_MINT, {'from': accounts[0]})
    tx_sell = chi_uniswap.tokenToEthSwapInput(TOKENS_MINT, 1, 9999999999, {'from': accounts[0]})
    out += f"        CHI: {str(tx_mint.gas_used + tx_sell.gas_used).ljust(6)} gas (mint and sell)\n"

    tx = lgt.mintToSell9630191(TOKENS_MINT, {'from': accounts[0]})
    out += f"        {color('dark green')}LGT: {str(tx.gas_used).ljust(6)} gas (mint and sell){color}\n"
    rpc.revert()

    # Burn Gas and Free
    out += f"\n  Burning {BURN} gas and freeing {TOKENS_FREE} tokens:\n"

    tx = h.burnAndFreeGST(BURN, TOKENS_FREE, {'from': accounts[0]})
    out += f"       GST2: {str(tx.gas_used).ljust(6)} gas (free from owned)\n"
    tx = h.burnAndFreeCHI(BURN, TOKENS_FREE, {'from': accounts[0]})
    out += f"        CHI: {str(tx.gas_used).ljust(6)} gas (free from owned)\n"
    price = lgt.getEthToTokenOutputPrice(TOKENS_FREE)
    tx = h.burnAndFree(BURN, TOKENS_FREE, {'from': accounts[0]})
    out += f"        {color('dark green')}LGT: {str(tx.gas_used).ljust(6)} gas (free from owned){color}\n"
    rpc.revert()

    # Buy Tokens Burn Gas And Free
    out += f"\n  Buying {TOKENS_FREE} tokens on Uniswap, then burning {BURN} gas and freeing the tokens:\n"

    price = gst_uniswap.getEthToTokenOutputPrice(TOKENS_FREE)
    tx_buy = gst_uniswap.ethToTokenSwapOutput(TOKENS_FREE, 9999999999, {'from': accounts[0], 'value': price})
    tx_free = h.burnAndFreeGST(BURN, TOKENS_FREE, {'from': accounts[0]})
    out += f"       GST2: {str(tx_buy.gas_used + tx_free.gas_used).ljust(6)} gas (buy and free)\n"

    price = chi_uniswap.getEthToTokenOutputPrice(TOKENS_FREE)
    tx_buy = chi_uniswap.ethToTokenSwapOutput(TOKENS_FREE, 9999999999, {'from': accounts[0], 'value': price})
    tx_free = h.burnAndFreeCHI(BURN, TOKENS_FREE, {'from': accounts[0]})
    out += f"        CHI: {str(tx_buy.gas_used + tx_free.gas_used).ljust(6)} gas (buy and free)\n"

    price = lgt.getEthToTokenOutputPrice(TOKENS_FREE)
    tx = h.burnBuyAndFreeOpt(BURN, TOKENS_FREE, {'from': accounts[0], 'value': price})
    out += f"        {color('dark green')}LGT: {str(tx.gas_used).ljust(6)} gas (buy and free){color}\n"
    rpc.revert()

    print(out)
    network.disconnect()
