import { task } from "hardhat/config";

task("balance", "Address escrow balance")
  .addPositionalParam("address", "Address to check balance")
  .setAction(async (taskArgs, hre) => {
    const escrow = await hre.ethers.getContractAt(
      "EscrowNative",
      process.env.ESCROW_ADDRESS!
    );

    const balance = await escrow.balanceOf(taskArgs.address);
    console.log(`Balance of ${taskArgs.address} is ${balance.toString()} (${hre.ethers.formatEther(balance)} TBNB)`);
  });
