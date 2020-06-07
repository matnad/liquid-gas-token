import brownie


def test_no_eth_to_sell_reverts(lgt, accounts):
    with brownie.reverts('dev: no eth to sell'):
        lgt.getEthToTokenInputPrice(0)


def test_no_tokens_to_sell_reverts(lgt, accounts):
    with brownie.reverts("dev: can't sell less than one token"):
        lgt.getTokenToEthInputPrice(0)
