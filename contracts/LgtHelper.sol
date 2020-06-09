pragma solidity ^0.6.7;

import "../interfaces/ILGT.sol";
import "../interfaces/IGST.sol";
import "../interfaces/ICHI.sol";

contract LgtHelper {
    uint256 public c = 1;

    ILGT public constant lgt = ILGT(0x000000000049091F98692b2460500B6D133ae31F);
    ICHI public constant chi = ICHI(0x0000000000004946c0e9F43F4Dee607b0eF1fA1c);
    IGST public constant gst = IGST(0x0000000000b3F879cb30FE243b4Dfee438691c04);

    function burnGas(uint256 burn) public returns (uint256 burned) {
        uint256 start = gasleft();
        assert(start > burn + 200);
        uint256 end = start - burn;
        while (gasleft() > end + 5000) {
            c++;
        }
        while(gasleft() > end) {}
        burned = start - gasleft();
    }

    function burnAndFree(uint256 burn, uint256 tokenAmount) public returns (bool success) {
        burnGas(burn);
        return lgt.freeFrom(tokenAmount, msg.sender);
    }

    function burnAndFreeGST(uint256 burn, uint256 tokenAmount) public returns (bool success) {
        burnGas(burn);
        return gst.freeFrom(msg.sender, tokenAmount);
    }

    function burnAndFreeCHI(uint256 burn, uint256 tokenAmount) public returns (uint256) {
        burnGas(burn);
        return chi.freeFrom(msg.sender, tokenAmount);
    }

    function burnBuyAndFree(uint256 burn, uint256 tokenAmount)
        public payable returns (uint256 ethSold)
    {
        burnGas(burn);
        return lgt.buyAndFree{value: msg.value}(tokenAmount, now, msg.sender);
    }

    function burnBuyAndFreeOpt(uint256 burn, uint256 tokenAmount) public payable {
        burnGas(burn);
        lgt.buyAndFree22457070633{value: msg.value}(tokenAmount);
    }

    function burnBuyUpToAndFree(uint256 burn, uint256 tokenAmount)
        public payable returns (uint256 ethSold)
    {
        burnGas(burn);
        return lgt.buyUpToAndFree{value: msg.value}(tokenAmount, now);
    }
}
