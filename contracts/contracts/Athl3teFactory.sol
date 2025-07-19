// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Athl3teDeploymentHelper {
    event CoreDeployed(address indexed core, address indexed deployer);
    event BotsDeployed(address indexed bots, address indexed deployer);
    event CommunitiesDeployed(address indexed communities, address indexed deployer);
    event NFTDeployed(address indexed nft, address indexed deployer);

    // Simple registry to keep track of deployed contracts
    struct DeploymentSet {
        address core;
        address bots;
        address communities;
        address nft;
        address deployer;
    }

    mapping(address => DeploymentSet) public deployments;
    address[] public deployers;

    function recordDeployment(
        address core,
        address bots,
        address communities,
        address nft
    ) external {
        deployments[msg.sender] = DeploymentSet({
            core: core,
            bots: bots,
            communities: communities,
            nft: nft,
            deployer: msg.sender
        });

        // Add to deployers list if first time
        bool isNewDeployer = true;
        for (uint i = 0; i < deployers.length; i++) {
            if (deployers[i] == msg.sender) {
                isNewDeployer = false;
                break;
            }
        }
        if (isNewDeployer) {
            deployers.push(msg.sender);
        }
    }

    function getDeployment(address deployer) external view returns (DeploymentSet memory) {
        return deployments[deployer];
    }

    function getAllDeployers() external view returns (address[] memory) {
        return deployers;
    }
}
