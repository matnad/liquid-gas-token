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

In addition to the usual mint and free functions LGT offers functions to very efficiently do multiple actions in one transaction:
 * mint and sell
 * mint and add to liquidity
 * buy and free
 
The full interface can be seen here: [ILGT](https://github.com/matnad/liquid-gas-token/blob/master/interfaces/ILGT.sol), [ILiquidERC20](https://github.com/matnad/liquid-gas-token/blob/master/interfaces/ILiquidERC20.sol), [IERC20](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol)

Gas price arbitrage can very easily be realized by minting LGT and directly receiving ether in return in the same transaction. This function is open to every user (and bot ;-)).

## Benchmarks

Comparative benchmarks for GST2, CHI and LGT. For GST2 and CHI, uniswap is used to do the buying and selling, LGT uses its own liquidity pool.

This does not give a full representation of gas cost, just a snapshot with the used token amounts. Care has been taken that all variables are initialized and the comparison is as fair as possible.

The tests were run with a Brownie Script on a ganache forked main net. You can see the script and details [here](https://github.com/matnad/liquid-gas-token/blob/master/scripts/benchmarks/gas_token_comparison.py). To replicate, clone the repo and run `brownie run benchmarks/gas_token_comparison --network mainnet-fork`.

    Minting 4 tokens:
       GST2: 179564 gas (mint to balance)
        CHI: 180463 gas (mint to balance)
        LGT: 185045 gas (mint to balance)

    Minting 4 tokens and selling them on Uniswap:
       GST2: 245360 gas (mint and sell)
        CHI: 246548 gas (mint and sell)
        LGT: 183214 gas (mint and sell)
    
    Burning 1000000 gas and freeing 25 tokens:
       GST2: 609178 gas (free from owned)
        CHI: 599767 gas (free from owned)
        LGT: 598055 gas (free from owned)

    Buying 25 tokens on Uniswap, then burning 1000000 gas and freeing the tokens:
       GST2: 661449 gas (buy and free)
        CHI: 651093 gas (buy and free)
        LGT: 592585 gas (buy and free)
        
LGT is optimized to buy or sell tokens in the same transaction they are freed or minted. 
In these metrics it vastly outperforms the alternatives.

## This repository is still a work in progress

The contract will be deployed on the test and main nets soon.

To run tests or scripts, clone the repo and use 

    brownie test tests/unit/ -C -n auto
    brownie test tests/integration/ -n auto --network mainnet-fork
    
or  
    
    brownie run path/to/script --network mainnet-fork 
