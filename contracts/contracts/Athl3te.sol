// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./interfaces/IAthl3teStructs.sol";
import "./interfaces/IAthl3teEvents.sol";
import "./libraries/UserLib.sol";
import "./libraries/BotLib.sol";
import "./libraries/CommunityLib.sol";
import "./libraries/ArrayUtils.sol";

contract Athl3te is ERC721, Ownable, ReentrancyGuard, IAthl3teEvents {
    using UserLib for IAthl3teStructs.User;
    using BotLib for mapping(string => IAthl3teStructs.Bot);
    using CommunityLib for mapping(string => IAthl3teStructs.CommunityRoom);
    using ArrayUtils for string[];

    uint256 private _tokenIdCounter;
    uint256 private messageIdGenerator;
    
    mapping(address => IAthl3teStructs.User) private users;
    mapping(string => IAthl3teStructs.Bot) private bots;
    mapping(string => IAthl3teStructs.CommunityRoom) private communityRooms;
    mapping(uint256 => string) private _tokenURIs;

    string[] private allBotNames;
    address[] private allUsers;
    string[] private allCommunityNames;

    modifier onlyRegistered() {
        require(users[msg.sender].isRegistered, "Not registered");
        _;
    }

    constructor(string memory name, string memory symbol) ERC721(name, symbol) Ownable() {
        _tokenIdCounter = 1; // Start token IDs from 1
    }

    function mintNftWithUri(string memory uri) external onlyRegistered {
        require(bytes(uri).length > 0, "URI cannot be empty");
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        _mint(msg.sender, tokenId);
        _tokenURIs[tokenId] = uri;
        users[msg.sender].addNft(tokenId);
        emit Minted(msg.sender, tokenId, uri);
    }

    function getNftUri(uint256 tokenId) external view returns (string memory) {
        return _tokenURIs[tokenId];
    }

    // User management functions
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

    // Bot management functions (only owner)
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

    function buyBot(string calldata _botName) external payable onlyRegistered nonReentrant {
        require(bots.exists(_botName), "Bot does not exist");
        require(msg.value >= bots.getCost(_botName), "Insufficient payment");

        messageIdGenerator++;
        users[msg.sender].addPurchasedAssistant(_botName, messageIdGenerator);
        emit BotPurchased(msg.sender, _botName, messageIdGenerator);
    }

    function createCommunityRoom(
        string calldata _communityName,
        string calldata _communityImage,
        string calldata _botName
    ) external onlyRegistered {
        require(bots.exists(_botName), "Bot does not exist");
        
        messageIdGenerator++;
        communityRooms.createRoom(_communityName, _communityImage, _botName, msg.sender, messageIdGenerator);
        allCommunityNames.push(_communityName);
        users[msg.sender].joinCommunity(_communityName);
        emit CommunityRoomCreated(_communityName, msg.sender, _botName, messageIdGenerator);
    }

    function joinCommunityRoom(string calldata _communityName) external onlyRegistered {
        communityRooms.joinRoom(_communityName, msg.sender);
        users[msg.sender].joinCommunity(_communityName);
        emit CommunityRoomJoined(msg.sender, _communityName);
    }

    function getUserCommunities() external view onlyRegistered returns (string[] memory)  {
        return users[msg.sender].joinedCommunities;
    }

    function getCommunityRoomDetails(string calldata _communityName) external view returns (IAthl3teStructs.CommunityRoom memory) {
        require(communityRooms.exists(_communityName), "Community does not exist");
        return communityRooms[_communityName];
    }

    function getBotDetails(string calldata _botName) external view returns (IAthl3teStructs.Bot memory) {
        require(bots.exists(_botName), "Bot does not exist");
        return bots[_botName];
    }

    function getAllBotNames() external view returns (string[] memory) {
        return allBotNames;
    }

    function getAllUsers() external view returns (address[] memory) {
        return allUsers;
    }

    function getAllCommunityNames() external view returns (string[] memory) {
        return allCommunityNames;
    }

    function getUserPersonalAssistant(address _userAddress) external view onlyRegistered returns (IAthl3teStructs.PersonalAssistant[] memory) {
        return users[_userAddress].purchasedAssistants;
    }

    // Owner functions
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        (bool success, ) = payable(owner()).call{value: balance}("");
        require(success, "Withdrawal failed");
    }

    function emergencyWithdraw(address payable _to) external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        (bool success, ) = _to.call{value: balance}("");
        require(success, "Emergency withdrawal failed");
    }

    // View functions for better data access
    function getUserCount() external view returns (uint256) {
        return allUsers.length;
    }

    function getBotCount() external view returns (uint256) {
        return allBotNames.length;
    }

    function getCommunityCount() external view returns (uint256) {
        return allCommunityNames.length;
    }

    function getCommunityMembers(string calldata _communityName) external view returns (address[] memory) {
        return communityRooms.getMembers(_communityName);
    }

    function isUserRegistered(address _user) external view returns (bool) {
        return users[_user].isRegistered;
    }

    function getUserNftCount(address _user) external view returns (uint256) {
        return users[_user].nftTokenIds.length;
    }

    // Override tokenURI to use our custom URI storage
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(ownerOf(tokenId) != address(0), "Token does not exist");
        return _tokenURIs[tokenId];
    }
}