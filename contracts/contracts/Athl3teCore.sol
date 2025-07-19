// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IAthl3teStructs.sol";
import "./interfaces/IAthl3teEvents.sol";
import "./libraries/UserLib.sol";

contract Athl3teCore is IAthl3teEvents {
    using UserLib for IAthl3teStructs.User;

    mapping(address => IAthl3teStructs.User) public users;
    address[] public allUsers;

    modifier onlyRegistered() {
        require(users[msg.sender].isRegistered, "Not registered");
        _;
    }

    function registerUser(string calldata _metadata) external {
        require(!users[msg.sender].isRegistered, "User already registered");
        require(bytes(_metadata).length > 0, "Metadata cannot be empty");

        IAthl3teStructs.User storage newUser = users[msg.sender];
        newUser.isRegistered = true;
        newUser.metadata = _metadata;

        allUsers.push(msg.sender);
        emit UserRegistered(msg.sender, _metadata);
    }

    function addActivity(string calldata _activityId) external onlyRegistered {
        users[msg.sender].addActivity(_activityId);
        emit ActivityAdded(msg.sender, _activityId);
    }

    function addSportGoal(string calldata _goalId) external onlyRegistered {
        users[msg.sender].addSportGoal(_goalId);
        emit SportGoalAdded(msg.sender, _goalId);
    }

    function addNutritionGoal(string calldata _goalId) external onlyRegistered {
        users[msg.sender].addNutritionGoal(_goalId);
        emit NutritionGoalAdded(msg.sender, _goalId);
    }

    function updateInjury(string calldata _injuryId) external onlyRegistered {
        users[msg.sender].updateInjury(_injuryId);
        emit InjuryUpdated(msg.sender, _injuryId);
    }

    function getUserDetails() external view onlyRegistered returns (IAthl3teStructs.User memory) {
        return users[msg.sender];
    }

    function getUserDetails(address _userAddress) external view returns (IAthl3teStructs.User memory) {
        require(users[_userAddress].isRegistered, "User not registered");
        return users[_userAddress];
    }

    function getAllUsers() external view returns (address[] memory) {
        return allUsers;
    }

    function getUserCount() external view returns (uint256) {
        return allUsers.length;
    }

    function isUserRegistered(address _user) external view returns (bool) {
        return users[_user].isRegistered;
    }
}
