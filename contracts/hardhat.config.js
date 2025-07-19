require('dotenv').config();
require('@nomiclabs/hardhat-ethers');
require('@nomiclabs/hardhat-waffle');

const deployerPrivateKey = process.env.WALLET_PRIVATE_KEY;


module.exports = {
  solidity: "0.8.20", 
  networks: {
    etherlinkTestnet: {
      url: "https://node.ghostnet.etherlink.com",
      accounts: [deployerPrivateKey],
    },
  },
  gasReporter: {
    enabled: true,
    currency: 'USD',
  },
};