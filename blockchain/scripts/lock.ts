import { task } from "hardhat/config";

task("lock", "Lock tokens to an address")
  .addPositionalParam("address", "Address to lock tokens")
  .addPositionalParam("amount", "Amount of tokens to deposit (in ether)")
  .setAction(async (taskArgs, hre) => {
    const escrow = await hre.ethers.getContractAt(
      "EscrowNative",
      process.env.ESCROW_ADDRESS!
    );

    const wallet = new hre.ethers.Wallet(process.env.DEPLOYER_PRIVATE_KEY!, hre.ethers.provider);
    console.log("Connected to wallet:", await wallet.getAddress());

    console.log("Locking...");
    const tx1 = await escrow
      .connect(wallet)
      .lock(taskArgs.address, hre.ethers.parseEther(taskArgs.amount));
    await tx1.wait();

    console.log("Done.");
  });
