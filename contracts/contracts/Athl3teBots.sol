// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./interfaces/IAthl3teStructs.sol";
import "./interfaces/IAthl3teEvents.sol";
import "./libraries/BotLib.sol";
import "./libraries/ArrayUtils.sol";

// Interface to interact with core contract
interface IAthl3teCore {
    function users(address user) external view returns (IAthl3teStructs.User memory);
    function isUserRegistered(address user) external view returns (bool);
}

contract Athl3teBots is Ownable, ReentrancyGuard, IAthl3teEvents {
    using BotLib for mapping(string => IAthl3teStructs.Bot);
    using ArrayUtils for string[];

    mapping(string => IAthl3teStructs.Bot) public bots;
    string[] public allBotNames;
    uint256 public messageIdGenerator;

    address public coreContract;

    modifier onlyRegistered() {
        require(IAthl3teCore(coreContract).isUserRegistered(msg.sender), "Not registered");
        _;
    }

    constructor(address _coreContract) Ownable() {
        coreContract = _coreContract;
    }

    function addBot(string calldata _botName, uint256 _unlockCostInWei) external onlyOwner {
        bots.createBot(_botName, _unlockCostInWei);
        allBotNames.push(_botName);
    }
    
    function updateBotCost(string calldata _botName, uint256 _newCost) external onlyOwner {
        bots.updateCost(_botName, _newCost);
    }
    
    function removeBot(string calldata _botName) external onlyOwner {
        bots.removeBot(_botName);
        allBotNames.removeString(_botName);
    }

    function buyBot(string calldata _botName) external payable onlyRegistered nonReentrant returns (uint256) {
        require(bots.exists(_botName), "Bot does not exist");
        require(msg.value >= bots.getCost(_botName), "Insufficient payment");

        messageIdGenerator++;
        emit BotPurchased(msg.sender, _botName, messageIdGenerator);
        return messageIdGenerator;
    }

    function getBotDetails(string calldata _botName) external view returns (IAthl3teStructs.Bot memory) {
        require(bots.exists(_botName), "Bot does not exist");
        return bots[_botName];
    }

    function getAllBotNames() external view returns (string[] memory) {
        return allBotNames;
    }

    function getBotCount() external view returns (uint256) {
        return allBotNames.length;
    }

    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "Withdrawal failed");
    }
}
