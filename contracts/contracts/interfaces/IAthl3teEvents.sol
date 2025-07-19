// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IAthl3teEvents {
    event UserRegistered(address indexed userAddress, string metadata);
    event ActivityAdded(address indexed userAddress, string activityId);
    event SportGoalAdded(address indexed userAddress, string goalId);
    event NutritionGoalAdded(address indexed userAddress, string goalId);
    event BotPurchased(address indexed userAddress, string botName, uint256 messagesId);
    event InjuryUpdated(address indexed userAddress, string injuryId);
    event CommunityRoomCreated(string indexed communityName, address indexed creator, string botName, uint256 messagesId);
    event CommunityRoomJoined(address indexed userAddress, string communityName);
    event Minted(address indexed owner, uint256 indexed tokenId, string tokenUri);
}
