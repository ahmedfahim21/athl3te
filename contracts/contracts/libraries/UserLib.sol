// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IAthl3teStructs.sol";

library UserLib {
    using UserLib for IAthl3teStructs.User;

    function addActivity(IAthl3teStructs.User storage user, string calldata _activityId) internal {
        require(bytes(_activityId).length > 0, "Activity ID cannot be empty");
        user.activityIds.push(_activityId);
    }

    function addSportGoal(IAthl3teStructs.User storage user, string calldata _goalId) internal {
        require(bytes(_goalId).length > 0, "Goal ID cannot be empty");
        user.sportGoalIds.push(_goalId);
    }

    function addNutritionGoal(IAthl3teStructs.User storage user, string calldata _goalId) internal {
        require(bytes(_goalId).length > 0, "Goal ID cannot be empty");
        user.nutritionGoalIds.push(_goalId);
    }

    function updateInjury(IAthl3teStructs.User storage user, string calldata _injuryId) internal {
        require(bytes(_injuryId).length > 0, "Injury ID cannot be empty");
        user.injuriesDescriptionId = _injuryId;
    }

    function addNft(IAthl3teStructs.User storage user, uint256 tokenId) internal {
        user.nftTokenIds.push(tokenId);
    }

    function addPurchasedAssistant(
        IAthl3teStructs.User storage user, 
        string calldata botName, 
        uint256 messageId
    ) internal {
        user.purchasedAssistants.push(IAthl3teStructs.PersonalAssistant({
            botName: botName,
            messagesId: messageId
        }));
    }

    function joinCommunity(IAthl3teStructs.User storage user, string calldata communityName) internal {
        user.joinedCommunities.push(communityName);
    }
}
