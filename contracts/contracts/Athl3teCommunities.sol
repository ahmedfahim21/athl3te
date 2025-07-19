// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IAthl3teStructs.sol";
import "./interfaces/IAthl3teEvents.sol";
import "./libraries/CommunityLib.sol";
import "./libraries/ArrayUtils.sol";

// Interface to interact with core contract
interface IAthl3teCore {
    function isUserRegistered(address user) external view returns (bool);
}

// Interface to interact with bots contract
interface IAthl3teBots {
    function bots(string calldata botName) external view returns (IAthl3teStructs.Bot memory);
}

contract Athl3teCommunities is IAthl3teEvents {
    using CommunityLib for mapping(string => IAthl3teStructs.CommunityRoom);
    using ArrayUtils for string[];

    mapping(string => IAthl3teStructs.CommunityRoom) public communityRooms;
    string[] public allCommunityNames;
    uint256 public messageIdGenerator;

    address public coreContract;
    address public botsContract;

    modifier onlyRegistered() {
        require(IAthl3teCore(coreContract).isUserRegistered(msg.sender), "Not registered");
        _;
    }

    constructor(address _coreContract, address _botsContract) {
        coreContract = _coreContract;
        botsContract = _botsContract;
    }

    function createCommunityRoom(
        string calldata _communityName,
        string calldata _communityImage,
        string calldata _botName
    ) external onlyRegistered {
        // Check if bot exists
        IAthl3teStructs.Bot memory bot = IAthl3teBots(botsContract).bots(_botName);
        require(bot.exists, "Bot does not exist");
        
        messageIdGenerator++;
        communityRooms.createRoom(_communityName, _communityImage, _botName, msg.sender, messageIdGenerator);
        allCommunityNames.push(_communityName);
        emit CommunityRoomCreated(_communityName, msg.sender, _botName, messageIdGenerator);
    }

    function joinCommunityRoom(string calldata _communityName) external onlyRegistered {
        communityRooms.joinRoom(_communityName, msg.sender);
        emit CommunityRoomJoined(msg.sender, _communityName);
    }

    function getCommunityRoomDetails(string calldata _communityName) external view returns (IAthl3teStructs.CommunityRoom memory) {
        require(communityRooms.exists(_communityName), "Community does not exist");
        return communityRooms[_communityName];
    }

    function getAllCommunityNames() external view returns (string[] memory) {
        return allCommunityNames;
    }

    function getCommunityCount() external view returns (uint256) {
        return allCommunityNames.length;
    }

    function getCommunityMembers(string calldata _communityName) external view returns (address[] memory) {
        return communityRooms.getMembers(_communityName);
    }
}
