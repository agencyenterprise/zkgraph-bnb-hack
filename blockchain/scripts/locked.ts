import { task } from "hardhat/config";

task("locked", "Address escrow locked balance")
  .addPositionalParam("address", "Address to check balance")
  .setAction(async (taskArgs, hre) => {
    const escrow = await hre.ethers.getContractAt(
      "EscrowNative",
      process.env.ESCROW_ADDRESS!
    );

    const balance = await escrow.lockedOf(taskArgs.address);
    console.log(`Balance locked of ${taskArgs.address} is ${balance.toString()} (${hre.ethers.formatEther(balance)} TBNB)`);
  });
