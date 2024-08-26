import { task } from "hardhat/config";

task("get-config", "Get the configuration of the contract")
  .setAction(async (taskArgs, hre) => {
    const escrow = await hre.ethers.getContractAt(
      "EscrowNative",
      process.env.ESCROW_ADDRESS!
    );

    console.log("platformFeePercentage:", hre.ethers.formatEther(await escrow.platformFeePercentage()));
    console.log("relayer:", await escrow.relayer());
    console.log("fees:", hre.ethers.formatEther(await escrow.fees()));
  });
