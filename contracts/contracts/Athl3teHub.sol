// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./interfaces/IAthl3teStructs.sol";

interface IAthl3teCore {
    function registerUser(string calldata _metadata) external;
    function addActivity(string calldata _activityId) external;
    function addSportGoal(string calldata _goalId) external;
    function addNutritionGoal(string calldata _goalId) external;
    function updateInjury(string calldata _injuryId) external;
    function getUserDetails() external view returns (IAthl3teStructs.User memory);
    function getUserDetails(address _userAddress) external view returns (IAthl3teStructs.User memory);
    function getAllUsers() external view returns (address[] memory);
    function isUserRegistered(address _user) external view returns (bool);
}

interface IAthl3teBots {
    function addBot(string calldata _botName, uint256 _unlockCostInWei) external;
    function updateBotCost(string calldata _botName, uint256 _newCost) external;
    function removeBot(string calldata _botName) external;
    function buyBot(string calldata _botName) external payable returns (uint256);
    function getBotDetails(string calldata _botName) external view returns (IAthl3teStructs.Bot memory);
    function getAllBotNames() external view returns (string[] memory);
    function withdraw() external;
}

interface IAthl3teCommunities {
    function createCommunityRoom(string calldata _communityName, string calldata _communityImage, string calldata _botName) external;
    function joinCommunityRoom(string calldata _communityName) external;
    function getCommunityRoomDetails(string calldata _communityName) external view returns (IAthl3teStructs.CommunityRoom memory);
    function getAllCommunityNames() external view returns (string[] memory);
    function getCommunityMembers(string calldata _communityName) external view returns (address[] memory);
}

interface IAthl3teNFT {
    function mintNftWithUri(string memory uri) external returns (uint256);
    function getNftUri(uint256 tokenId) external view returns (string memory);
    function tokenURI(uint256 tokenId) external view returns (string memory);
    function balanceOf(address owner) external view returns (uint256);
}

/**
 * @title Athl3teHub
 * @dev Central hub contract that provides unified interface to all Athl3te modules
 * This contract doesn't store data but routes calls to appropriate contracts
 */
contract Athl3teHub {
    address public immutable coreContract;
    address public immutable botsContract;
    address public immutable communitiesContract;
    address public immutable nftContract;
    address public immutable viewContract;

    event ModulesConnected(
        address core,
        address bots,
        address communities,
        address nft,
        address viewAddr
    );

    constructor(
        address _coreContract,
        address _botsContract,
        address _communitiesContract,
        address _nftContract,
        address _viewContract
    ) {
        coreContract = _coreContract;
        botsContract = _botsContract;
        communitiesContract = _communitiesContract;
        nftContract = _nftContract;
        viewContract = _viewContract;

        emit ModulesConnected(_coreContract, _botsContract, _communitiesContract, _nftContract, _viewContract);
    }

    // User functions - route to core
    function registerUser(string calldata _metadata) external {
        IAthl3teCore(coreContract).registerUser(_metadata);
    }

    function addActivity(string calldata _activityId) external {
        IAthl3teCore(coreContract).addActivity(_activityId);
    }

    function addSportGoal(string calldata _goalId) external {
        IAthl3teCore(coreContract).addSportGoal(_goalId);
    }

    function addNutritionGoal(string calldata _goalId) external {
        IAthl3teCore(coreContract).addNutritionGoal(_goalId);
    }

    function updateInjury(string calldata _injuryId) external {
        IAthl3teCore(coreContract).updateInjury(_injuryId);
    }

    // Bot functions - route to bots contract
    function buyBot(string calldata _botName) external payable returns (uint256) {
        return IAthl3teBots(botsContract).buyBot{value: msg.value}(_botName);
    }

    // Community functions - route to communities contract
    function createCommunityRoom(
        string calldata _communityName,
        string calldata _communityImage,
        string calldata _botName
    ) external {
        IAthl3teCommunities(communitiesContract).createCommunityRoom(_communityName, _communityImage, _botName);
    }

    function joinCommunityRoom(string calldata _communityName) external {
        IAthl3teCommunities(communitiesContract).joinCommunityRoom(_communityName);
    }

    // NFT functions - route to NFT contract
    function mintNftWithUri(string memory uri) external returns (uint256) {
        return IAthl3teNFT(nftContract).mintNftWithUri(uri);
    }

    // View functions - aggregate from multiple contracts
    function getUserDetails() external view returns (IAthl3teStructs.User memory) {
        return IAthl3teCore(coreContract).getUserDetails();
    }

    function getBotDetails(string calldata _botName) external view returns (IAthl3teStructs.Bot memory) {
        return IAthl3teBots(botsContract).getBotDetails(_botName);
    }

    function getCommunityRoomDetails(string calldata _communityName) external view returns (IAthl3teStructs.CommunityRoom memory) {
        return IAthl3teCommunities(communitiesContract).getCommunityRoomDetails(_communityName);
    }

    function getAllBotNames() external view returns (string[] memory) {
        return IAthl3teBots(botsContract).getAllBotNames();
    }

    function getAllCommunityNames() external view returns (string[] memory) {
        return IAthl3teCommunities(communitiesContract).getAllCommunityNames();
    }

    function getAllUsers() external view returns (address[] memory) {
        return IAthl3teCore(coreContract).getAllUsers();
    }

    function isUserRegistered(address _user) external view returns (bool) {
        return IAthl3teCore(coreContract).isUserRegistered(_user);
    }

    function getUserNftCount(address _user) external view returns (uint256) {
        return IAthl3teNFT(nftContract).balanceOf(_user);
    }

    // Get all contract addresses for frontend integration
    function getContractAddresses() external view returns (
        address core,
        address bots,
        address communities,
        address nft,
        address viewAddr
    ) {
        return (coreContract, botsContract, communitiesContract, nftContract, viewContract);
    }
}
