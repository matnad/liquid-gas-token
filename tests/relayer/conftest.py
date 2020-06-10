import pytest


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(1, 51, 99999999999, {'from': accounts[0], 'value': "0.05 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[1], 'value': "0.049 ether"})
    yield lgt


@pytest.fixture(scope="module")
def relayer(accounts, LGTRelayer):
    yield accounts[0].deploy(LGTRelayer)


@pytest.fixture(scope="module")
def helper(accounts, LgtHelper):
    yield accounts[0].deploy(LgtHelper)


@pytest.fixture(scope="module")
def storage(accounts, liquid_lgt, Contract):
    storage_bytecode = "0x6080604052600560005534801561001557600080fd5b5060e3806100246000396000f3fe60806040526004361060305760003560e01c806360fe47b11460355780636d4ce63c14605d578063bc25bd20146081575b600080fd5b348015604057600080fd5b50605b60048036036020811015605557600080fd5b5035609b565b005b348015606857600080fd5b50606f60a0565b60408051918252519081900360200190f35b605b60048036036020811015609557600080fd5b503560a6565b600055565b60005490565b503460005556fea2646970667358221220f24d2143601b1aae859f1a7cd42f132a90acc23593aa210b7c23e868eb26601264736f6c63430006090033"
    storage_abi = [
        {
            "inputs": [],
            "name": "get",
            "outputs": [
                {
                    "internalType": "uint256",
                    "name": "",
                    "type": "uint256"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "_x",
                    "type": "uint256"
                }
            ],
            "name": "set",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {
                    "internalType": "uint256",
                    "name": "_x",
                    "type": "uint256"
                }
            ],
            "name": "setPayable",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        }
    ]
    tx = liquid_lgt.deploy(0, 99999999999999, storage_bytecode, {'from': accounts[0], 'value': "1 ether"})
    address = tx.return_value
    yield Contract.from_abi(name="Storage", address=address, abi=storage_abi, owner=accounts[0])
