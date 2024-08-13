import hre from "hardhat";

async function main() {
  console.log("Deploying...");
  const Escrow = await hre.ethers.getContractFactory("EscrowNative");
  const escrow = await Escrow.deploy();

  console.log("Contract deployed at:", await escrow.getAddress());
}

main().catch((error) => {
  console.log(error);
  process.exitCode = 1;
});
