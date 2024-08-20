import hre from "hardhat";

async function main() {
  console.log("Deploying...");
  const EscrowNative = await hre.ethers.getContractFactory("EscrowNative");
  const escrowNative = await EscrowNative.deploy(hre.ethers.parseEther("1"), process.env.DEFENDER_RELAYER_ADDRESS!);

  console.log("Contract deployed at:", await escrowNative.getAddress());
}

main().catch((error) => {
  console.log(error);
  process.exitCode = 1;
});
