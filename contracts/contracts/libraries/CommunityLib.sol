// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../interfaces/IAthl3teStructs.sol";

library CommunityLib {
    function createRoom(
        mapping(string => IAthl3teStructs.CommunityRoom) storage communityRooms,
        string calldata _communityName,
        string calldata _communityImage,
        string calldata _botName,
        address _creator,
        uint256 _messageId
    ) internal {
        require(bytes(_communityName).length > 0, "Community name cannot be empty");
        require(bytes(communityRooms[_communityName].communityName).length == 0, "Community already exists");

        IAthl3teStructs.CommunityRoom storage room = communityRooms[_communityName];
        room.communityName = _communityName;
        room.communityImage = _communityImage;
        room.botName = _botName;
        room.messagesId = _messageId;
        room.createdBy = _creator;
        room.members.push(_creator);
    }

    function joinRoom(
        mapping(string => IAthl3teStructs.CommunityRoom) storage communityRooms,
        string calldata _communityName,
        address _user
    ) internal {
        IAthl3teStructs.CommunityRoom storage room = communityRooms[_communityName];
        require(bytes(room.communityName).length > 0, "Community room does not exist");

        // Check if user is already a member
        bool isMember = false;
        for (uint256 i = 0; i < room.members.length; i++) {
            if (room.members[i] == _user) {
                isMember = true;
                break;
            }
        }
        require(!isMember, "Already a member");

        room.members.push(_user);
    }

    function exists(
        mapping(string => IAthl3teStructs.CommunityRoom) storage communityRooms,
        string calldata _communityName
    ) internal view returns (bool) {
        return bytes(communityRooms[_communityName].communityName).length > 0;
    }

    function getMembers(
        mapping(string => IAthl3teStructs.CommunityRoom) storage communityRooms,
        string calldata _communityName
    ) internal view returns (address[] memory) {
        require(bytes(communityRooms[_communityName].communityName).length > 0, "Community does not exist");
        return communityRooms[_communityName].members;
    }
}
