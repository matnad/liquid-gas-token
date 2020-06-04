pragma solidity ^0.6.7;

import "../interfaces/ILGT.sol";
import "../interfaces/IGST.sol";
import "../interfaces/ICHI.sol";

contract LgtHelper {
    uint256 public c = 1;

    function burnGas(uint256 burn) public returns (uint256 burned){
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
        return ILGT(0x00000000007475142d6329FC42Dc9684c9bE6cD0).freeFrom(tokenAmount, msg.sender);
    }

    function freeAndBurn(uint256 burn, uint256 tokenAmount) public returns (bool success) {
        success =  ILGT(0x00000000007475142d6329FC42Dc9684c9bE6cD0).freeFrom(tokenAmount, msg.sender);
        burnGas(burn);
    }

    function burnAndFreeGST(uint256 burn, uint256 tokenAmount) public returns (bool success) {
        burnGas(burn);
        return IGST(0x0000000000b3F879cb30FE243b4Dfee438691c04).freeFrom(msg.sender, tokenAmount);
    }

    function burnAndFreeCHI(uint256 burn, uint256 tokenAmount) public returns (uint256) {
        burnGas(burn);
        return ICHI(0x0000000000004946c0e9F43F4Dee607b0eF1fA1c).freeFrom(msg.sender, tokenAmount);
    }

    function burnBuyAndFree(uint256 burn, uint256 tokenAmount) public payable returns (uint256 ethSold) {
        burnGas(burn);
        return ILGT(0x00000000007475142d6329FC42Dc9684c9bE6cD0).buyAndFree{value: msg.value}(tokenAmount, now + 1, msg.sender);
    }

    function burnBuyUpToAndFree(uint256 burn, uint256 tokenAmount) public payable returns (uint256 ethSold) {
        burnGas(burn);
        return ILGT(0x00000000007475142d6329FC42Dc9684c9bE6cD0).buyUpToAndFree{value: msg.value}(tokenAmount, now + 1);
    }
}
