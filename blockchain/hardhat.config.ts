import * as dotenv from "dotenv";
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

import "./scripts/deposit";
import "./scripts/lock";
import "./scripts/balance";
import "./scripts/locked";
import "./scripts/get-config";

dotenv.config();

const DEPLOYER_PRIVATE_KEY: any = process.env.DEPLOYER_PRIVATE_KEY;

const config: HardhatUserConfig = {
  solidity: "0.8.24",
  networks: {
    bsctestnet: {
      url: "https://data-seed-prebsc-2-s3.binance.org:8545/",
      chainId: 97,
      accounts: [DEPLOYER_PRIVATE_KEY]
    },
  },
};

export default config;
