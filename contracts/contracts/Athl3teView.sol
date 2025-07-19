// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IAthl3teStructs.sol";

// Interface to interact with main contract
interface IAthl3teMain {
    function getAllUsers() external view returns (address[] memory);
    function getAllBotNames() external view returns (string[] memory);
    function getAllCommunityNames() external view returns (string[] memory);
    function isUserRegistered(address user) external view returns (bool);
    function getUserDetails(address user) external view returns (IAthl3teStructs.User memory);
    function getBotDetails(string calldata botName) external view returns (IAthl3teStructs.Bot memory);
    function getCommunityRoomDetails(string calldata communityName) external view returns (IAthl3teStructs.CommunityRoom memory);
}

contract Athl3teView {
    address public immutable mainContract;
    
    constructor(address _mainContract) {
        mainContract = _mainContract;
    }

    // Advanced view functions
    function getUsersByActivity(string calldata activityType) external view returns (address[] memory) {
        IAthl3teMain main = IAthl3teMain(mainContract);
        address[] memory allUsers = main.getAllUsers();
        address[] memory matchingUsers = new address[](allUsers.length);
        uint256 count = 0;

        for (uint256 i = 0; i < allUsers.length; i++) {
            if (main.isUserRegistered(allUsers[i])) {
                IAthl3teStructs.User memory user = main.getUserDetails(allUsers[i]);
                for (uint256 j = 0; j < user.activityIds.length; j++) {
                    if (keccak256(bytes(user.activityIds[j])) == keccak256(bytes(activityType))) {
                        matchingUsers[count] = allUsers[i];
                        count++;
                        break;
                    }
                }
            }
        }

        // Resize array to actual count
        address[] memory result = new address[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = matchingUsers[i];
        }
        return result;
    }

    function getCommunitiesWithBot(string calldata botName) external view returns (string[] memory) {
        IAthl3teMain main = IAthl3teMain(mainContract);
        string[] memory allCommunities = main.getAllCommunityNames();
        string[] memory matchingCommunities = new string[](allCommunities.length);
        uint256 count = 0;

        for (uint256 i = 0; i < allCommunities.length; i++) {
            IAthl3teStructs.CommunityRoom memory room = main.getCommunityRoomDetails(allCommunities[i]);
            if (keccak256(bytes(room.botName)) == keccak256(bytes(botName))) {
                matchingCommunities[count] = allCommunities[i];
                count++;
            }
        }

        // Resize array to actual count
        string[] memory result = new string[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = matchingCommunities[i];
        }
        return result;
    }

    function getTotalCommunityMembers() external view returns (uint256) {
        IAthl3teMain main = IAthl3teMain(mainContract);
        string[] memory allCommunities = main.getAllCommunityNames();
        uint256 totalMembers = 0;

        for (uint256 i = 0; i < allCommunities.length; i++) {
            IAthl3teStructs.CommunityRoom memory room = main.getCommunityRoomDetails(allCommunities[i]);
            totalMembers += room.members.length;
        }

        return totalMembers;
    }

    function getUserStats(address userAddress) external view returns (
        uint256 activitiesCount,
        uint256 sportGoalsCount,
        uint256 nutritionGoalsCount,
        uint256 nftsCount,
        uint256 communitiesCount,
        uint256 botsCount
    ) {
        IAthl3teMain main = IAthl3teMain(mainContract);
        if (!main.isUserRegistered(userAddress)) {
            return (0, 0, 0, 0, 0, 0);
        }

        IAthl3teStructs.User memory user = main.getUserDetails(userAddress);
        return (
            user.activityIds.length,
            user.sportGoalIds.length,
            user.nutritionGoalIds.length,
            user.nftTokenIds.length,
            user.joinedCommunities.length,
            user.purchasedAssistants.length
        );
    }
}
