from tests.constants import *

INTEREST = ETH_DEPOSIT * INTEREST_FACTOR // 10000

def _test_add_liquidity(w3, eth_flash, assert_fail, add_liquidity):
    a0, a1, a2 = w3.eth.accounts[:3]
    assert_fail(lambda: w3.eth.sendTransaction({'to': eth_flash.address, 'value': 0, 'from': a1}))

    add_liquidity(a1, ETH_DEPOSIT)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    eth_flash.balanceOf(a1) == ETH_DEPOSIT

    add_liquidity(a1, ETH_DEPOSIT)
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 2
    assert eth_flash.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT * 2
    eth_flash.balanceOf(a1) == ETH_DEPOSIT * 2

def test_add_liquidity(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    add_liquidity = lambda _from, value: eth_flash.addLiquidity(transact={'value': value, 'from': _from})
    _test_add_liquidity(w3, eth_flash, assert_fail, add_liquidity)

def test_default(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    add_liquidity = lambda _from, value: w3.eth.sendTransaction({'to':eth_flash.address, 'value': value, 'from': _from})
    _test_add_liquidity(w3, eth_flash, assert_fail, add_liquidity)

def test_remove_liquidity_wo_flash(w3, eth_flash, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a2})

    assert_fail(lambda: eth_flash.removeLiquidity(ETH_DEPOSIT + 1, transact={'from': a1}))
    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert_fail(lambda: eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a0}))
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a2) == ETH_DEPOSIT
    assert_fail(lambda: eth_flash.removeLiquidity(1, transact={'from': a1}))

    assert_fail(lambda: eth_flash.removeLiquidity(ETH_DEPOSIT + 1, transact={'from': a2}))
    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2})
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.totalSupply() == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(a2) == INITIAL_ETH
    assert eth_flash.balanceOf(a2) == 0
    assert_fail(lambda: eth_flash.removeLiquidity(1, transact={'from': a2}))

def _init_test_flash(w3, eth_flash, a1):
    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT, 'from': a1})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT

def test_flash_good_lender(w3, eth_flash, good_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': good_lender.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT
    good_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT + INTEREST
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT - INTEREST

    eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a1})
    assert_fail(lambda: eth_flash.removeLiquidity(ETH_DEPOSIT, transact={'from': a2}))
    assert w3.eth.getBalance(eth_flash.address) == 0
    assert eth_flash.totalSupply() == 0
    assert w3.eth.getBalance(a1) == INITIAL_ETH + INTEREST
    assert eth_flash.balanceOf(a1) == 0
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT - INTEREST

def test_flash_bad_lender(w3, eth_flash, bad_lender, assert_fail):
    a0, a1, a2 = w3.eth.accounts[:3]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': bad_lender.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(bad_lender.address) == ETH_DEPOSIT
    assert_fail(lambda: bad_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={}))

def test_flash_with_liquidity(w3, eth_flash, good_lender, assert_fail):
    a0, a1, a2, a3 = w3.eth.accounts[:4]
    _init_test_flash(w3, eth_flash, a1)

    w3.eth.sendTransaction({'to': good_lender.address, 'value': ETH_DEPOSIT})
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT
    good_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT + INTEREST
    assert eth_flash.totalSupply() == ETH_DEPOSIT
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT - INTEREST

    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT + INTEREST, 'from': a2})
    assert w3.eth.getBalance(eth_flash.address) == (ETH_DEPOSIT + INTEREST) * 2
    assert eth_flash.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.balanceOf(a2) == ETH_DEPOSIT

    good_lender.flash_loan_eth(eth_flash.address, ETH_DEPOSIT, DEADLINE, transact={})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 2 + INTEREST * 3
    assert eth_flash.totalSupply() == ETH_DEPOSIT * 2
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.balanceOf(a2) == ETH_DEPOSIT
    assert w3.eth.getBalance(good_lender.address) == ETH_DEPOSIT - INTEREST * 2

    eth_flash.addLiquidity(transact={'value': ETH_DEPOSIT + INTEREST * 3 // 2, 'from': a3})
    assert w3.eth.getBalance(eth_flash.address) == ETH_DEPOSIT * 3 + INTEREST * 9 // 2
    assert eth_flash.totalSupply() == ETH_DEPOSIT * 3
    assert w3.eth.getBalance(a1) == INITIAL_ETH - ETH_DEPOSIT
    assert eth_flash.balanceOf(a1) == ETH_DEPOSIT
    assert w3.eth.getBalance(a2) == INITIAL_ETH - ETH_DEPOSIT - INTEREST
    assert eth_flash.balanceOf(a2) == ETH_DEPOSIT
    assert w3.eth.getBalance(a3) == INITIAL_ETH - ETH_DEPOSIT - INTEREST * 3 // 2
    assert eth_flash.balanceOf(a3) == ETH_DEPOSIT