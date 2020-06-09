// SPDX-License-Identifier: MIT
pragma solidity ^0.6.7;

import "../interfaces/ILGT.sol";

contract TestModifier {
    uint private c = 1;
    address public constant LGT = 0x00000000007475142d6329FC42Dc9684c9bE6cD0;

    modifier refund() {
	  uint initialGas = gasleft();
	  _;
	  uint t = (initialGas - gasleft() + 19560) / 41717;
	  if (t > 0) {
	  	c = ILGT(LGT).getEthToTokenOutputPrice(t);
	  	if (c < ((17717 * t) - 19560) * tx.gasprice) {
	  	  ILGT(LGT).buyAndFree{value: msg.value}(t, now + 1, msg.sender);
	  	}
	  }
	}

    function expensiveRefund(uint n) public payable refund {
        for (uint i = 0; i < n; i++) {
            c = i;
        }
    }

    function expensiveNoRefund(uint n) public {
        for (uint i = 0; i < n; i++) {
            c = i;
        }
    }
}
