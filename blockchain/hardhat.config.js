require("@nomicfoundation/hardhat-ethers");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    // Red local levantada por `hardhat node` dentro del mismo contenedor
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
};
