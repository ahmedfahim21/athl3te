const { ethers } = require("hardhat");
require("dotenv").config();

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log(`Deploying contract with account: ${deployer.address}`);

    // Deploy the contract
    const contract = await ethers.getContractFactory("Athl3te");
    const athl3te = await contract.deploy("Athl3te NFT", "ATH3");

    await athl3te.deployed();
    console.log(`Contract deployed to: ${athl3te.address}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });