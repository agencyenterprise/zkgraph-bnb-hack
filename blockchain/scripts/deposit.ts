import { task } from "hardhat/config";

task("deposit", "Deposit tokens to an address")
  .addPositionalParam("from", "Private key depositing the tokens")
  .addPositionalParam("amount", "Amount of tokens to deposit (in ether)")
  .setAction(async (taskArgs, hre) => {
    const escrow = await hre.ethers.getContractAt(
      "Escrow",
      process.env.ESCROW_ADDRESS!
    );
    const token = await hre.ethers.getContractAt(
      "MockERC20Token",
      process.env.TOKEN_ADDRESS!
    );

    const wallet = new hre.ethers.Wallet(taskArgs.from, hre.ethers.provider);
    console.log("Connected to wallet:", await wallet.getAddress());

    console.log("Approving...");
    const tx1 = await token
      .connect(wallet)
      .approve(
        process.env.ESCROW_ADDRESS!,
        hre.ethers.parseEther(taskArgs.amount)
      );
    await tx1.wait();

    console.log("Depositing...");
    const tx2 = await escrow
      .connect(wallet)
      .deposit(hre.ethers.parseEther(taskArgs.amount));
    await tx2.wait();

    console.log("Done.");
  });
