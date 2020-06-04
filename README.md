# The Liquid Gas Token

**Master Thesis Project of Matthias Nadler, University of Basel**

**Supervised by:**  
**Prof. Dr. Fabian Schär**  
Credit Suisse Asset Management (Schweiz) Professor for Distributed Ledger Technologies and   
Fintech Center for Innovative Finance, University of Basel

## A short introduction

The Liquid Gas Token (LGT) combines an ERC20 Gas Token (as popularized by [gastoken.io](https://gastoken.io/) and later 
[1inch.exchange's CHI](https://github.com/CryptoManiacsZone/chi)) 
with an internal liquidity pool, very similar to [Uniswap V1](https://github.com/Uniswap/uniswap-v1).

The LGT's liquidity pool token reserve is implicitly defined as the amount of *"unowned"* tokens.  
This allows for very efficient minting and freeing of tokens when combined with ownership transfers.

For example, it costs less gas to buy and free `n` LGT tokens than to simply `freeFrom(n)` GST2 tokens.

Liquidity can be built by directly minting to the liquidity pool, which needs zero ownership changes of the tokens and costs less gas then simply minting a token would.

Gas price arbitrage can be realized by anyone with minting LGT and directly receiving ether in return. Again, without any ownership changes.

## This repository is still a work in progress

To run tests or scripts, you need add the LGT Deployer account (LGT needs to be deployed at a 15 bytes address):
```bash
brownie accounts import gst_deployer keystore/gst_deployer.json 
```
Or set an *environment variable* `GST_DEPLOYER=<private key>`.

Run tests with `brownie test tests/unit/ -s`.

`tests/unit/` can be run on a local test net.  
`tests/gas/` require a forked main net. 
