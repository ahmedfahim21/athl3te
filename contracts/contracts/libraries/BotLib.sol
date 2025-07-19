// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IAthl3teStructs.sol";

library BotLib {
    function createBot(
        mapping(string => IAthl3teStructs.Bot) storage bots,
        string calldata _botName, 
        uint256 _unlockCostInWei
    ) internal {
        require(bytes(_botName).length > 0, "Bot name cannot be empty");
        require(!bots[_botName].exists, "Bot already exists");
        
        bots[_botName] = IAthl3teStructs.Bot({
            botName: _botName,
            unlockCostInWei: _unlockCostInWei,
            exists: true
        });
    }

    function updateCost(
        mapping(string => IAthl3teStructs.Bot) storage bots,
        string calldata _botName, 
        uint256 _newCost
    ) internal {
        require(bots[_botName].exists, "Bot does not exist");
        bots[_botName].unlockCostInWei = _newCost;
    }

    function removeBot(
        mapping(string => IAthl3teStructs.Bot) storage bots,
        string calldata _botName
    ) internal {
        require(bots[_botName].exists, "Bot does not exist");
        delete bots[_botName];
    }

    function exists(
        mapping(string => IAthl3teStructs.Bot) storage bots,
        string calldata _botName
    ) internal view returns (bool) {
        return bots[_botName].exists;
    }

    function getCost(
        mapping(string => IAthl3teStructs.Bot) storage bots,
        string calldata _botName
    ) internal view returns (uint256) {
        require(bots[_botName].exists, "Bot does not exist");
        return bots[_botName].unlockCostInWei;
    }
}
