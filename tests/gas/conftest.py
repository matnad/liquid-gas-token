#!/usr/bin/python3

import pytest
from brownie import project


@pytest.fixture(scope="module")
def liquid_lgt(lgt, accounts):
    lgt.mint(150, {'from': accounts[0]})
    lgt.addLiquidity(1, 150, 99999999999, {'from': accounts[0], 'value': "0.149 ether"})
    lgt.mint(120, {'from': accounts[1]})
    lgt.addLiquidity(1, 100, 99999999999, {'from': accounts[1], 'value': "0.099 ether"})
    yield lgt


@pytest.fixture(scope="module")
def uniswap_gst():
    interface = project.get_loaded_projects()[0].interface
    # yield Contract.from_explorer("0x929507CD3D90Ab11eC4822E9eB5A48eb3a178F19")
    yield interface.UniswapExchangeInterface("0x929507CD3D90Ab11eC4822E9eB5A48eb3a178F19")


@pytest.fixture(scope="module")
def gst2(accounts):
    interface = project.get_loaded_projects()[0].interface
    gst = interface.IGST("0x0000000000b3F879cb30FE243b4Dfee438691c04")
    gst.mint(50, {'from': accounts[0]})
    gst.mint(50, {'from': accounts[1]})
    yield gst


@pytest.fixture(scope="module")
def chi(accounts):
    interface = project.get_loaded_projects()[0].interface
    chi = interface.IGST("0x0000000000004946c0e9F43F4Dee607b0eF1fA1c")
    chi.mint(50, {'from': accounts[0]})
    chi.mint(50, {'from': accounts[1]})
    yield chi


@pytest.fixture(scope="module")
def uniswap_chi(chi, accounts):
    interface = project.get_loaded_projects()[0].interface
    # Fund the chi exchange
    chi.mint(150, {'from': accounts[9]})
    unichi = interface.UniswapExchangeInterface("0xD772f5ac5c4145f3B2b460515d277f667253E6Dc")
    chi.approve(unichi, 2 ** 256 - 1, {'from': accounts[9]})
    unichi.addLiquidity(1, 150, 99999999999, {'from': accounts[9], 'value': "0.04 ether"})
    yield unichi


@pytest.fixture(scope="module")
def helper(LgtHelper, gst2, liquid_lgt, chi, accounts):
    lgtHelper = accounts[0].deploy(LgtHelper)
    for a in accounts[:6]:
        liquid_lgt.approve(lgtHelper, 2**256-1, {'from': a})
        gst2.approve(lgtHelper, 2 ** 256 - 1, {'from': a})
        chi.approve(lgtHelper, 2 ** 256 - 1, {'from': a})
    yield lgtHelper
