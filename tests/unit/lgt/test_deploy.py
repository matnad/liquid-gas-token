import brownie
import pytest

DEADLINE = 99999999999
storage_bytecode = "0x6080604052600560005534801561001557600080fd5b5060ac806100246000" \
                   "396000f3fe6080604052348015600f57600080fd5b5060043610603257600035" \
                   "60e01c806360fe47b11460375780636d4ce63c146053575b600080fd5b605160" \
                   "048036036020811015604b57600080fd5b5035606b565b005b60596070565b60" \
                   "408051918252519081900360200190f35b600055565b6000549056fea2646970" \
                   "667358221220da99a6a9d4cea3f86897beaabcc36a956a9de39ec09abb36fa08" \
                   "6b5e25243df164736f6c63430006070033"
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
    }
]


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.mint(50, {'from': accounts[0]})
    lgt.addLiquidity(1, 51, 99999999999, {'from': accounts[0], 'value': "0.05 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, 99999999999, {'from': accounts[1], 'value': "0.049 ether"})
    yield lgt


def test_deploy(liquid_lgt, accounts, Contract):
    initial_tokens = liquid_lgt.poolTokenReserves()
    price = liquid_lgt.getEthToTokenOutputPrice(5)
    tx = liquid_lgt.deploy(5, DEADLINE, storage_bytecode, {'from': accounts[0], 'value': price})
    address = tx.return_value
    contract = Contract.from_abi(name="Storage", address=address, abi=storage_abi, owner=accounts[0])
    assert contract.get() == 5
    contract.set(10)
    assert contract.get() == 10
    assert initial_tokens - 5 == liquid_lgt.poolTokenReserves()


def test_deploy_refund(liquid_lgt, accounts):
    initial_balance = accounts[0].balance()
    price = liquid_lgt.getEthToTokenOutputPrice(5)
    liquid_lgt.deploy(5, DEADLINE, storage_bytecode, {'from': accounts[0], 'value': price * 2})
    assert initial_balance - price == accounts[0].balance()


def test_deploy_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.deploy(5, 1, storage_bytecode, {'from': accounts[0], 'value': "1 ether"})


def test_create2(liquid_lgt, accounts, Contract):
    initial_tokens = liquid_lgt.poolTokenReserves()
    price = liquid_lgt.getEthToTokenOutputPrice(4)
    tx = liquid_lgt.create2(4, DEADLINE, "0xabc", storage_bytecode, {'from': accounts[0], 'value': price})
    address = tx.return_value
    contract = Contract.from_abi(name="Storage", address=address, abi=storage_abi, owner=accounts[0])
    assert contract.get() == 5
    contract.set(10)
    assert contract.get() == 10
    assert initial_tokens - 4 == liquid_lgt.poolTokenReserves()


def test_create2_refund(liquid_lgt, accounts):
    initial_balance = accounts[0].balance()
    price = liquid_lgt.getEthToTokenOutputPrice(3)
    liquid_lgt.create2(3, DEADLINE, "0xabc", storage_bytecode, {'from': accounts[0], 'value': price * 2})
    assert initial_balance - price == accounts[0].balance()


def test_create2_deadline_reverts(liquid_lgt, accounts):
    with brownie.reverts("dev: deadline passed"):
        liquid_lgt.create2(4, 1, "0xabc", storage_bytecode, {'from': accounts[0], 'value': "1 ether"})
