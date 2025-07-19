// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IAthl3teStructs {
    struct Bot {
        string botName;
        uint256 unlockCostInWei;
        bool exists;
    }

    struct PersonalAssistant {
        string botName;
        uint256 messagesId;
    }

    struct User {
        string metadata;
        string[] activityIds;
        string[] sportGoalIds;
        string[] nutritionGoalIds;
        PersonalAssistant[] purchasedAssistants;
        string injuriesDescriptionId;
        uint256[] nftTokenIds;
        bool isRegistered;
        string[] joinedCommunities;
    }

    struct CommunityRoom {
        string communityName;
        string communityImage;
        string botName;
        address createdBy;
        uint256 messagesId;
        address[] members;
    }
}
