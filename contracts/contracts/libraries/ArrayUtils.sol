// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

library ArrayUtils {
    function removeString(string[] storage array, string calldata value) internal {
        for (uint256 i = 0; i < array.length; i++) {
            if (keccak256(bytes(array[i])) == keccak256(bytes(value))) {
                array[i] = array[array.length - 1];
                array.pop();
                break;
            }
        }
    }

    function containsString(string[] storage array, string calldata value) internal view returns (bool) {
        for (uint256 i = 0; i < array.length; i++) {
            if (keccak256(bytes(array[i])) == keccak256(bytes(value))) {
                return true;
            }
        }
        return false;
    }
}
