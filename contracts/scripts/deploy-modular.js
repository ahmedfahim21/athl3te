const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Starting Athl3te Modular Deployment...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const deployedContracts = {};

  try {
    // 1. Deploy Core Contract
    console.log("\n📦 Deploying Athl3teCore...");
    const Athl3teCore = await ethers.getContractFactory("Athl3teCore");
    const coreContract = await Athl3teCore.deploy();
    await coreContract.deployed();
    deployedContracts.core = coreContract.address;
    console.log("✅ Athl3teCore deployed to:", coreContract.address);

    // 2. Deploy Bots Contract
    console.log("\n📦 Deploying Athl3teBots...");
    const Athl3teBots = await ethers.getContractFactory("Athl3teBots");
    const botsContract = await Athl3teBots.deploy(coreContract.address);
    await botsContract.deployed();
    deployedContracts.bots = botsContract.address;
    console.log("✅ Athl3teBots deployed to:", botsContract.address);

    // 3. Deploy Communities Contract
    console.log("\n📦 Deploying Athl3teCommunities...");
    const Athl3teCommunities = await ethers.getContractFactory("Athl3teCommunities");
    const communitiesContract = await Athl3teCommunities.deploy(
      coreContract.address,
      botsContract.address
    );
    await communitiesContract.deployed();
    deployedContracts.communities = communitiesContract.address;
    console.log("✅ Athl3teCommunities deployed to:", communitiesContract.address);

    // 4. Deploy NFT Contract
    console.log("\n📦 Deploying Athl3teNFT...");
    const Athl3teNFT = await ethers.getContractFactory("Athl3teNFT");
    const nftContract = await Athl3teNFT.deploy(
      "Athl3te NFT",
      "ATH3NFT",
      coreContract.address
    );
    await nftContract.deployed();
    deployedContracts.nft = nftContract.address;
    console.log("✅ Athl3teNFT deployed to:", nftContract.address);

    // 5. Deploy View Contract (optional, for analytics)
    console.log("\n📦 Deploying Athl3teView...");
    const Athl3teView = await ethers.getContractFactory("Athl3teView");
    const viewContract = await Athl3teView.deploy(coreContract.address);
    await viewContract.deployed();
    deployedContracts.view = viewContract.address;
    console.log("✅ Athl3teView deployed to:", viewContract.address);

    // 6. Deploy Registry Helper
    console.log("\n📦 Deploying Athl3teDeploymentHelper...");
    const Athl3teDeploymentHelper = await ethers.getContractFactory("Athl3teDeploymentHelper");
    const helperContract = await Athl3teDeploymentHelper.deploy();
    await helperContract.deployed();
    deployedContracts.helper = helperContract.address;
    console.log("✅ Athl3teDeploymentHelper deployed to:", helperContract.address);

    // 7. Deploy Hub Contract (central interface)
    console.log("\n📦 Deploying Athl3teHub...");
    const Athl3teHub = await ethers.getContractFactory("Athl3teHub");
    const hubContract = await Athl3teHub.deploy(
      coreContract.address,
      botsContract.address,
      communitiesContract.address,
      nftContract.address,
      viewContract.address
    );
    await hubContract.deployed();
    deployedContracts.hub = hubContract.address;
    console.log("✅ Athl3teHub deployed to:", hubContract.address);

    // 8. Record deployment in helper contract
    console.log("\n📝 Recording deployment in helper...");
    await helperContract.recordDeployment(
      coreContract.address,
      botsContract.address,
      communitiesContract.address,
      nftContract.address
    );

    console.log("\n🎉 All contracts deployed successfully!");
    console.log("\n📋 Contract Addresses:");
    console.log("==========================================");
    for (const [name, address] of Object.entries(deployedContracts)) {
      console.log(`${name.toUpperCase().padEnd(15)}: ${address}`);
    }

    console.log("\n🌟 Main Integration Point:");
    console.log(`HUB CONTRACT    : ${deployedContracts.hub}`);
    console.log("👆 Use this address for frontend integration");

  } catch (error) {
    console.error("\n❌ Deployment failed:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
